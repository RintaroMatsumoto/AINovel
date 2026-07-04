"""
ComfyUI リモート生成デスクトップアプリ
M1 Mac Mini (Docker ComfyUI) に接続して画像生成
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import requests, json, time, os, threading, urllib.parse, urllib.request
from datetime import datetime

# ─── デフォルト設定 ───
DEFAULT_HOST = "100.112.59.35"
DEFAULT_PORT = "18188"
DEFAULT_CKPT = "yayoi_mix.safetensors"
DEFAULT_RES = "512×768"
DEFAULT_STEPS = 28
DEFAULT_CFG = 7.0
DEFAULT_SAMPLER = "dpmpp_2m"
DEFAULT_SCHEDULER = "karras"
DEFAULT_LORA1 = "JapaneseDollLikeness_v15.safetensors"
DEFAULT_LORA1_STR = 0.5
DEFAULT_LORA2 = "DetailTweaker.safetensors"
DEFAULT_LORA2_STR = 0.2
DEFAULT_FACEID_WEIGHT = 0.8
DEFAULT_NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
               "cartoon, anime, illustration, painting, 3d render, cgi, "
               "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
               "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
               "watermark, signature, text, logo, existing celebrity, real person, copyrighted character")

DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")

# ─── プリセット ───
PRESETS = {}

def register_presets():
    global PRESETS
    PRESETS = {
        "栞13歳_百合子seed": {
            "base": ("(masterpiece, best quality:1.2), 8k, RAW photo, "
                     "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
                     "13 year old japanese girl, second year middle school student, "
                     "round childish face, baby fat still visible, "
                     "small thin build, still growing, "
                     "long straight black hair, neat bangs"),
            "neg": DEFAULT_NEG + ", adult, mature, old, aging, wrinkles, heavy makeup, dark eyeshadow, lipstick, dyed hair, colored hair, blonde hair, brown hair",
            "seed": "5977", "cfg": "7.0", "steps": "28", "use_faceid": False,
            "ckpt": DEFAULT_CKPT, "lora1": DEFAULT_LORA1, "lora1s": str(DEFAULT_LORA1_STR),
            "lora2": DEFAULT_LORA2, "lora2s": str(DEFAULT_LORA2_STR),
        },
        "栞13歳_誠seed": {
            "base": ("(masterpiece, best quality:1.2), 8k, RAW photo, "
                     "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
                     "13 year old japanese girl, second year middle school student, "
                     "round childish face, baby fat still visible, "
                     "small thin build, still growing, "
                     "long straight black hair, neat bangs"),
            "neg": DEFAULT_NEG + ", adult, mature, old, aging, wrinkles, heavy makeup, dark eyeshadow, lipstick, dyed hair, colored hair, blonde hair, brown hair",
            "seed": "1193774", "cfg": "7.0", "steps": "28", "use_faceid": False,
            "ckpt": DEFAULT_CKPT, "lora1": DEFAULT_LORA1, "lora1s": str(DEFAULT_LORA1_STR),
            "lora2": DEFAULT_LORA2, "lora2s": str(DEFAULT_LORA2_STR),
        },
        "百合子18歳_FaceID": {
            "base": ("(masterpiece, best quality:1.2), 8k, RAW photo, "
                     "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
                     "japanese young woman, 18 years old, petite small frame, plain natural face"),
            "neg": DEFAULT_NEG + ", makeup, frills, lace, ribbon, curly hair, wavy hair, low ponytail, long ponytail, hair past shoulders, long hair",
            "seed": "random", "cfg": "7.0", "steps": "28", "use_faceid": True,
            "faceid_weight": "0.8", "faceid_ref": "",
            "ckpt": DEFAULT_CKPT, "lora1": DEFAULT_LORA1, "lora1s": "0.5",
            "lora2": DEFAULT_LORA2, "lora2s": "0.2",
        },
        "誠40歳_IPAdapter": {
            "base": ("(masterpiece, best quality:1.2), 8k, RAW photo, "
                     "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
                     "japanese man, in his 40s, section manager, salaryman, "
                     "masculine face, strong jawline, sharp features, clean shaven, "
                     "natural salt and pepper hair, neatly combed side part, "
                     "slight gray at temples, subtle silver strands, "
                     "(silver thin metal frame glasses:1.1), "
                     "tired eyes, weary gaze, exhausted expression, "
                     "dark circles under eyes, slight hollow under eyes, "
                     "subdued expression, quiet weariness"),
            "neg": DEFAULT_NEG + ", feminine, woman, female features, androgynous, soft face, delicate, pretty, girly, effeminate, ambiguous gender, curly hair, wavy hair, colored hair, long hair, pompadour, quiff, slicked back, heavy wax, excessive volume, sharp sideburns, host style, flashy hair, gel hair, spiky hair, extreme two block, undercut, beard, full beard, long stubble, goatee, facial hair, black suit, funeral, mourning, young, smooth skin, radiant, fresh-faced, glowing, vibrant, energetic, healthy, different person, face changed, identity change",
            "seed": "random", "cfg": "7.5", "steps": "28", "use_faceid": False,
            "use_ipadapter": True, "ip_weight": "0.45", "ip_ref": "",
            "ckpt": DEFAULT_CKPT, "lora1": "", "lora1s": "0.0",
            "lora2": "", "lora2s": "0.0",
        },
    }


class ComfyUIGUI:
    def __init__(self, root):
        self.root = root
        root.title("ComfyUI Remote Generator")
        root.geometry("1100x780")

        # ─── 変数 ───
        self.host_var = tk.StringVar(value=DEFAULT_HOST)
        self.port_var = tk.StringVar(value=DEFAULT_PORT)
        self.ckpt_var = tk.StringVar(value=DEFAULT_CKPT)
        self.lora1_var = tk.StringVar(value=DEFAULT_LORA1)
        self.lora1s_var = tk.StringVar(value=str(DEFAULT_LORA1_STR))
        self.lora2_var = tk.StringVar(value=DEFAULT_LORA2)
        self.lora2s_var = tk.StringVar(value=str(DEFAULT_LORA2_STR))
        self.base_var = tk.StringVar()
        self.neg_var = tk.StringVar(value=DEFAULT_NEG)
        self.seed_var = tk.StringVar(value="random")
        self.cfg_var = tk.StringVar(value=str(DEFAULT_CFG))
        self.steps_var = tk.StringVar(value=str(DEFAULT_STEPS))
        self.res_var = tk.StringVar(value=DEFAULT_RES)
        self.out_var = tk.StringVar(value=DESKTOP)
        self.use_faceid_var = tk.BooleanVar(value=False)
        self.faceid_w_var = tk.StringVar(value=str(DEFAULT_FACEID_WEIGHT))
        self.faceid_ref_var = tk.StringVar(value="")
        self.use_ip_var = tk.BooleanVar(value=False)
        self.ip_w_var = tk.StringVar(value="0.45")
        self.ip_ref_var = tk.StringVar(value="")
        self.batch_var = tk.IntVar(value=1)
        self.generating = False
        self.variants = []

        # ─── プリセット登録 ───
        register_presets()

        # ─── Notebook ───
        nb = ttk.Notebook(root)
        nb.pack(fill="both", expand=True, padx=5, pady=5)

        # タブ1: 生成
        self.build_gen_tab(nb)
        # タブ2: 設定
        self.build_config_tab(nb)
        # タブ3: プリセット
        self.build_preset_tab(nb)

        # ステータスバー
        self.status_var = tk.StringVar(value="Ready")
        sb = ttk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w")
        sb.pack(fill="x", padx=5, pady=2)

    # ──────── タブ1: 生成 ────────
    def build_gen_tab(self, nb):
        f = ttk.Frame(nb)
        nb.add(f, text="生成")
        f.columnconfigure(0, weight=1)
        f.rowconfigure(3, weight=1)

        # 上段: プロンプト
        pf = ttk.LabelFrame(f, text="プロンプト", padding=5)
        pf.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ttk.Label(pf, text="Base Prompt:").grid(row=0, column=0, sticky="w")
        self.base_entry = tk.Text(pf, height=3, wrap="word")
        self.base_entry.grid(row=1, column=0, columnspan=3, sticky="ew", pady=2)

        ttk.Label(pf, text="Negative Prompt:").grid(row=2, column=0, sticky="w")
        self.neg_entry = tk.Text(pf, height=3, wrap="word")
        self.neg_entry.grid(row=3, column=0, columnspan=3, sticky="ew", pady=2)

        # 中段左: バリアント一覧
        vf = ttk.LabelFrame(f, text="バリアント一覧（各項目をカンマ区切りで入力）", padding=5)
        vf.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        vf.columnconfigure(0, weight=1)
        vf.rowconfigure(1, weight=1)

        cols = ("#", "hair", "clothes", "pose")
        self.vtree = ttk.Treeview(vf, columns=cols, show="headings", height=6)
        self.vtree.heading("#", text="#")
        self.vtree.heading("hair", text="Hair")
        self.vtree.heading("clothes", text="Clothes")
        self.vtree.heading("pose", text="Pose/Angle")
        self.vtree.column("#", width=30)
        self.vtree.column("hair", width=250)
        self.vtree.column("clothes", width=300)
        self.vtree.column("pose", width=300)
        self.vtree.grid(row=0, column=0, sticky="nsew")

        vsb = ttk.Scrollbar(vf, orient="vertical", command=self.vtree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.vtree.configure(yscrollcommand=vsb.set)

        bf = ttk.Frame(vf)
        bf.grid(row=1, column=0, columnspan=2, sticky="ew", pady=2)
        ttk.Button(bf, text="＋ 追加", command=self.add_variant_dialog, width=12).pack(side="left", padx=2)
        ttk.Button(bf, text="－ 削除", command=self.del_variant, width=8).pack(side="left", padx=2)
        ttk.Button(bf, text="クリア", command=self.clear_variants, width=8).pack(side="left", padx=2)

        # 下段: 各種設定 + ボタン
        cf = ttk.Frame(f)
        cf.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        cf.columnconfigure(1, weight=1)

        ttk.Label(cf, text="Seed:").grid(row=0, column=0, sticky="w")
        self.seed_entry = tk.Entry(cf, textvariable=self.seed_var, width=14)
        self.seed_entry.grid(row=0, column=1, sticky="w", padx=2)

        ttk.Label(cf, text="CFG:").grid(row=0, column=2, sticky="w", padx=(10,0))
        self.cfg_spin = ttk.Spinbox(cf, from_=1.0, to=20.0, increment=0.5,
                                     textvariable=self.cfg_var, width=6)
        self.cfg_spin.grid(row=0, column=3, sticky="w")

        ttk.Label(cf, text="Steps:").grid(row=0, column=4, sticky="w", padx=(10,0))
        self.steps_spin = ttk.Spinbox(cf, from_=10, to=60, increment=1,
                                       textvariable=self.steps_var, width=6)
        self.steps_spin.grid(row=0, column=5, sticky="w")

        ttk.Label(cf, text="枚数:").grid(row=0, column=6, sticky="w", padx=(10,0))
        self.batch_spin = ttk.Spinbox(cf, from_=1, to=50, increment=1,
                                       textvariable=self.batch_var, width=5)
        self.batch_spin.grid(row=0, column=7, sticky="w")

        ttk.Label(cf, text="出力先:").grid(row=1, column=0, sticky="w", pady=2)
        self.out_entry = tk.Entry(cf, textvariable=self.out_var)
        self.out_entry.grid(row=1, column=1, columnspan=6, sticky="ew", padx=2)
        ttk.Button(cf, text="…", command=self.choose_out, width=3).grid(row=1, column=7)

        self.go_btn = ttk.Button(cf, text="🚀 一括生成", command=self.start_generation)
        self.go_btn.grid(row=2, column=0, columnspan=8, sticky="ew", pady=5)

        # ログ
        lf = ttk.LabelFrame(f, text="ログ", padding=5)
        lf.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        lf.columnconfigure(0, weight=1)
        lf.rowconfigure(0, weight=1)
        self.log_text = scrolledtext.ScrolledText(lf, height=8, state="disabled", wrap="word")
        self.log_text.grid(row=0, column=0, sticky="nsew")

    # ──────── タブ2: 設定 ────────
    def build_config_tab(self, nb):
        f = ttk.Frame(nb)
        nb.add(f, text="設定")

        # 接続設定
        cf = ttk.LabelFrame(f, text="接続設定", padding=5)
        cf.pack(fill="x", padx=5, pady=5)
        ttk.Label(cf, text="Host:").grid(row=0, column=0, sticky="w")
        ttk.Entry(cf, textvariable=self.host_var, width=20).grid(row=0, column=1, sticky="w", padx=2)
        ttk.Label(cf, text="Port:").grid(row=0, column=2, sticky="w", padx=(10,0))
        ttk.Entry(cf, textvariable=self.port_var, width=8).grid(row=0, column=3, sticky="w", padx=2)
        ttk.Button(cf, text="接続テスト", command=self.test_connection).grid(row=0, column=4, padx=(10,0))

        # モデル設定
        mf = ttk.LabelFrame(f, text="モデル設定", padding=5)
        mf.pack(fill="x", padx=5, pady=5)

        ttk.Label(mf, text="Checkpoint:").grid(row=0, column=0, sticky="w")
        ttk.Entry(mf, textvariable=self.ckpt_var, width=30).grid(row=0, column=1, sticky="w", padx=2)

        ttk.Label(mf, text="LoRA1:").grid(row=1, column=0, sticky="w")
        ttk.Entry(mf, textvariable=self.lora1_var, width=30).grid(row=1, column=1, sticky="w", padx=2)
        ttk.Label(mf, text="Strength:").grid(row=1, column=2, sticky="w", padx=(10,0))
        ttk.Entry(mf, textvariable=self.lora1s_var, width=6).grid(row=1, column=3, sticky="w")

        ttk.Label(mf, text="LoRA2:").grid(row=2, column=0, sticky="w")
        ttk.Entry(mf, textvariable=self.lora2_var, width=30).grid(row=2, column=1, sticky="w", padx=2)
        ttk.Label(mf, text="Strength:").grid(row=2, column=2, sticky="w", padx=(10,0))
        ttk.Entry(mf, textvariable=self.lora2s_var, width=6).grid(row=2, column=3, sticky="w")

        # FaceID設定
        ff = ttk.LabelFrame(f, text="FaceID 設定", padding=5)
        ff.pack(fill="x", padx=5, pady=5)
        ttk.Checkbutton(ff, text="FaceID を使用", variable=self.use_faceid_var).grid(row=0, column=0, sticky="w")
        ttk.Label(ff, text="Weight:").grid(row=0, column=1, sticky="w", padx=(10,0))
        ttk.Entry(ff, textvariable=self.faceid_w_var, width=6).grid(row=0, column=2, sticky="w")
        ttk.Label(ff, text="参照画像:").grid(row=1, column=0, sticky="w")
        ttk.Entry(ff, textvariable=self.faceid_ref_var, width=50).grid(row=1, column=1, columnspan=2, sticky="ew", padx=2)
        ttk.Button(ff, text="…", command=lambda: self.choose_file(self.faceid_ref_var), width=3).grid(row=1, column=3)

        # IPAdapter設定
        ipf = ttk.LabelFrame(f, text="IPAdapter 設定", padding=5)
        ipf.pack(fill="x", padx=5, pady=5)
        ttk.Checkbutton(ipf, text="IPAdapter を使用（通常版）", variable=self.use_ip_var).grid(row=0, column=0, sticky="w")
        ttk.Label(ipf, text="Weight:").grid(row=0, column=1, sticky="w", padx=(10,0))
        ttk.Entry(ipf, textvariable=self.ip_w_var, width=6).grid(row=0, column=2, sticky="w")
        ttk.Label(ipf, text="参照画像:").grid(row=1, column=0, sticky="w")
        ttk.Entry(ipf, textvariable=self.ip_ref_var, width=50).grid(row=1, column=1, columnspan=2, sticky="ew", padx=2)
        ttk.Button(ipf, text="…", command=lambda: self.choose_file(self.ip_ref_var), width=3).grid(row=1, column=3)

    # ──────── タブ3: プリセット ────────
    def build_preset_tab(self, nb):
        f = ttk.Frame(nb)
        nb.add(f, text="プリセット")

        ttk.Label(f, text="保存済みプリセットを選択して読み込み:").pack(anchor="w", padx=5, pady=5)

        self.preset_listbox = tk.Listbox(f, height=10)
        self.preset_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        for name in PRESETS:
            self.preset_listbox.insert("end", name)

        bf = ttk.Frame(f)
        bf.pack(fill="x", padx=5, pady=5)
        ttk.Button(bf, text="読み込み", command=self.load_preset).pack(side="left", padx=2)
        ttk.Button(bf, text="現在の設定をプリセット保存", command=self.save_preset).pack(side="left", padx=2)

    # ──────── ダイアログ ────────
    def add_variant_dialog(self):
        d = tk.Toplevel(self.root)
        d.title("バリアント追加")
        d.geometry("600x200")
        d.transient(self.root)
        d.grab_set()

        ttk.Label(d, text="Hair:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        hair_e = tk.Entry(d, width=70)
        hair_e.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(d, text="Clothes:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        clothes_e = tk.Entry(d, width=70)
        clothes_e.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(d, text="Pose:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        pose_e = tk.Entry(d, width=70)
        pose_e.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        def ok():
            h, c, p = hair_e.get().strip(), clothes_e.get().strip(), pose_e.get().strip()
            if h or c or p:
                self.variants.append((h, c, p))
                self.refresh_vtree()
            d.destroy()

        ttk.Button(d, text="追加", command=ok).grid(row=3, column=1, sticky="e", padx=5, pady=10)

    def del_variant(self):
        sel = self.vtree.selection()
        if not sel:
            return
        idx = int(self.vtree.item(sel[0], "values")[0]) - 1
        if 0 <= idx < len(self.variants):
            self.variants.pop(idx)
            self.refresh_vtree()

    def clear_variants(self):
        self.variants.clear()
        self.refresh_vtree()

    def refresh_vtree(self):
        for row in self.vtree.get_children():
            self.vtree.delete(row)
        for i, (h, c, p) in enumerate(self.variants, 1):
            self.vtree.insert("", "end", values=(i, h, c, p))

    def choose_out(self):
        d = filedialog.askdirectory(initialdir=self.out_var.get() or DESKTOP)
        if d:
            self.out_var.set(d)

    def choose_file(self, var):
        d = filedialog.askopenfilename(
            initialdir=os.path.dirname(var.get()) if var.get() else DESKTOP,
            filetypes=[("画像", "*.png *.jpg *.jpeg"), ("すべて", "*.*")]
        )
        if d:
            var.set(d)

    # ──────── プリセット操作 ────────
    def load_preset(self):
        sel = self.preset_listbox.curselection()
        if not sel:
            return
        name = self.preset_listbox.get(sel[0])
        p = PRESETS.get(name)
        if not p:
            return
        self.base_entry.delete("1.0", "end")
        self.base_entry.insert("1.0", p.get("base", ""))
        self.neg_entry.delete("1.0", "end")
        self.neg_entry.insert("1.0", p.get("neg", DEFAULT_NEG))
        self.seed_var.set(p.get("seed", "random"))
        self.cfg_var.set(p.get("cfg", str(DEFAULT_CFG)))
        self.steps_var.set(p.get("steps", str(DEFAULT_STEPS)))
        self.use_faceid_var.set(p.get("use_faceid", False))
        self.faceid_w_var.set(p.get("faceid_weight", str(DEFAULT_FACEID_WEIGHT)))
        self.faceid_ref_var.set(p.get("faceid_ref", ""))
        self.use_ip_var.set(p.get("use_ipadapter", False))
        self.ip_w_var.set(p.get("ip_weight", "0.45"))
        self.ip_ref_var.set(p.get("ip_ref", ""))
        self.ckpt_var.set(p.get("ckpt", DEFAULT_CKPT))
        self.lora1_var.set(p.get("lora1", DEFAULT_LORA1))
        self.lora1s_var.set(p.get("lora1s", str(DEFAULT_LORA1_STR)))
        self.lora2_var.set(p.get("lora2", DEFAULT_LORA2))
        self.lora2s_var.set(p.get("lora2s", str(DEFAULT_LORA2_STR)))
        self.log(f"プリセット '{name}' を読み込みました")

    def save_preset(self):
        d = tk.Toplevel(self.root)
        d.title("プリセット保存")
        d.geometry("300x100")
        d.transient(self.root)
        d.grab_set()
        ttk.Label(d, text="プリセット名:").pack(padx=5, pady=5)
        name_e = tk.Entry(d, width=40)
        name_e.pack(padx=5, pady=5)
        def ok():
            n = name_e.get().strip()
            if n:
                PRESETS[n] = {
                    "base": self.base_entry.get("1.0", "end-1c"),
                    "neg": self.neg_entry.get("1.0", "end-1c"),
                    "seed": self.seed_var.get(),
                    "cfg": self.cfg_var.get(),
                    "steps": self.steps_var.get(),
                    "use_faceid": self.use_faceid_var.get(),
                    "faceid_weight": self.faceid_w_var.get(),
                    "faceid_ref": self.faceid_ref_var.get(),
                    "use_ipadapter": self.use_ip_var.get(),
                    "ip_weight": self.ip_w_var.get(),
                    "ip_ref": self.ip_ref_var.get(),
                    "ckpt": self.ckpt_var.get(),
                    "lora1": self.lora1_var.get(),
                    "lora1s": self.lora1s_var.get(),
                    "lora2": self.lora2_var.get(),
                    "lora2s": self.lora2s_var.get(),
                }
                self.preset_listbox.insert("end", n)
                self.log(f"プリセット '{n}' を保存しました")
            d.destroy()
        ttk.Button(d, text="保存", command=ok).pack(pady=5)

    # ──────── ログ ────────
    def log(self, msg):
        self.log_text.configure(state="normal")
        t = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{t}] {msg}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        self.root.update_idletasks()

    def status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

    # ──────── 接続テスト ────────
    def test_connection(self):
        url = f"http://{self.host_var.get()}:{self.port_var.get()}/history"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                messagebox.showinfo("成功", f"M1 ComfyUI に接続成功 ✅")
            else:
                messagebox.showerror("エラー", f"HTTP {r.status_code}")
        except Exception as e:
            messagebox.showerror("エラー", f"接続失敗: {e}")

    # ──────── 生成 ────────
    def start_generation(self):
        if self.generating:
            return
        if not self.variants and not self.base_entry.get("1.0", "end-1c").strip():
            messagebox.showwarning("警告", "バリアントまたはBase Promptを入力してください")
            return
        self.generating = True
        self.go_btn.configure(text="⏹ 停止", command=self.stop_generation)
        threading.Thread(target=self._generate_loop, daemon=True).start()

    def stop_generation(self):
        self.generating = False
        self.go_btn.configure(text="🚀 一括生成", command=self.start_generation)
        self.log("ユーザーにより停止")

    def _generate_loop(self):
        base = self.base_entry.get("1.0", "end-1c").strip()
        neg = self.neg_entry.get("1.0", "end-1c").strip()
        out_dir = self.out_var.get().strip()
        if not out_dir:
            out_dir = DESKTOP
        os.makedirs(out_dir, exist_ok=True)

        seed_str = self.seed_var.get().strip()
        cfg = float(self.cfg_var.get())
        steps = int(self.steps_var.get())
        ckpt = self.ckpt_var.get()
        lora1 = self.lora1_var.get().strip()
        l1s = float(self.lora1s_var.get())
        lora2 = self.lora2_var.get().strip()
        l2s = float(self.lora2s_var.get())
        use_fid = self.use_faceid_var.get()
        use_ip = self.use_ip_var.get()

        total = len(self.variants) if self.variants else 1
        batch = self.batch_var.get()

        self.status(f"生成中... 0/{total * batch}")
        self.log(f"生成開始: {total} パターン × {batch} 枚")

        for vi in range(batch):
            if not self.generating:
                break
            for i, (hair, clothes, pose) in enumerate(self.variants if self.variants else [("", "", "")]):
                if not self.generating:
                    break
                tag = f"v{i+1:02d}_{vi+1:03d}"
                if hair and clothes and pose:
                    prompt = f"{base}, {hair}, {clothes}, {pose}"
                elif hair or clothes or pose:
                    parts = [p for p in (hair, clothes, pose) if p]
                    prompt = f"{base}, {', '.join(parts)}"
                else:
                    prompt = base

                resolved_seed = self._resolve_seed(seed_str)
                prefix = self._make_prefix(tag, resolved_seed)

                self.log(f"[{vi*batch+i+1}/{total*batch}] seed={resolved_seed} {tag}")
                self.status(f"生成中... {vi*batch+i+1}/{total*batch}")

                wf = self._build_wf(prompt, neg, resolved_seed, ckpt, lora1, l1s, lora2, l2s,
                                    cfg, steps, use_fid, use_ip, prefix)
                self._gen_one(wf, prefix, out_dir)
                time.sleep(0.3)

        self.generating = False
        self.go_btn.configure(text="🚀 一括生成", command=self.start_generation)
        self.status("完了")
        self.log(f"生成完了: {out_dir}")

    def _resolve_seed(self, s):
        if s.lower() == "random" or s == "":
            import random
            return random.randint(1000000000, 9999999999)
        return int(s)

    def _make_prefix(self, tag, seed):
        return f"gen_{datetime.now().strftime('%m%d_%H%M')}_s{seed}_{tag}"

    def _build_wf(self, prompt, neg, seed, ckpt, lora1, l1s, lora2, l2s,
                  cfg, steps, use_fid, use_ip, prefix):
        base_url = f"http://{self.host_var.get()}:{self.port_var.get()}"
        w = H = 512  # default
        try:
            rp = self.res_var.get().split("×")
            w, H = int(rp[0].strip()), int(rp[1].strip())
        except:
            w, H = 512, 768

        nodes = {}
        nid = 1

        # Checkpoint
        nodes[str(nid)] = {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}}
        nid += 1

        # LoRAs
        clip_conn = ["1", 1]
        model_conn = ["1", 0]
        if lora1:
            nodes[str(nid)] = {"class_type": "LoraLoader",
                               "inputs": {"model": model_conn, "clip": clip_conn,
                                          "lora_name": lora1, "strength_model": l1s, "strength_clip": l1s}}
            model_conn = [str(nid), 0]; clip_conn = [str(nid), 1]; nid += 1
        if lora2:
            nodes[str(nid)] = {"class_type": "LoraLoader",
                               "inputs": {"model": model_conn, "clip": clip_conn,
                                          "lora_name": lora2, "strength_model": l2s, "strength_clip": l2s}}
            model_conn = [str(nid), 0]; clip_conn = [str(nid), 1]; nid += 1

        final_model = model_conn

        # FaceID or IPAdapter
        if use_fid:
            ref_path = self.faceid_ref_var.get()
            ref_name = self._upload_ref(ref_path) if ref_path else None
            if ref_name:
                nodes[str(nid)] = {"class_type": "IPAdapterUnifiedLoaderFaceID",
                                   "inputs": {"model": final_model, "preset": "FACEID PLUS V2",
                                              "lora_strength": 0.5, "provider": "CPU"}}
                fid_loader = [str(nid), 0]; fid_ip = [str(nid), 1]; nid += 1
                nodes[str(nid)] = {"class_type": "LoadImage", "inputs": {"image": ref_name}}
                img_node = str(nid); nid += 1
                nodes[str(nid)] = {"class_type": "IPAdapterInsightFaceLoader",
                                   "inputs": {"provider": "CPU", "model_name": "buffalo_l"}}
                ins_node = str(nid); nid += 1
                nodes[str(nid)] = {"class_type": "IPAdapterFaceID",
                                   "inputs": {
                                       "model": fid_loader, "ipadapter": fid_ip, "image": [img_node, 0],
                                       "weight": float(self.faceid_w_var.get()), "weight_faceidv2": 0.0,
                                       "weight_type": "linear", "combine_embeds": "concat",
                                       "start_at": 0.0, "end_at": 1.0, "embeds_scaling": "V only",
                                       "insightface": [ins_node, 0]}}
                final_model = [str(nid), 0]; nid += 1

        elif use_ip:
            ref_path = self.ip_ref_var.get()
            ref_name = self._upload_ref(ref_path) if ref_path else None
            if ref_name:
                nodes[str(nid)] = {"class_type": "IPAdapterUnifiedLoader",
                                   "inputs": {"model": final_model, "preset": "STANDARD (medium strength)"}}
                ip_loader = [str(nid), 0]; ip_adp = [str(nid), 1]; nid += 1
                nodes[str(nid)] = {"class_type": "LoadImage", "inputs": {"image": ref_name}}
                img_node = str(nid); nid += 1
                nodes[str(nid)] = {"class_type": "IPAdapter",
                                   "inputs": {
                                       "model": ip_loader, "ipadapter": ip_adp, "image": [img_node, 0],
                                       "weight": float(self.ip_w_var.get()),
                                       "start_at": 0.0, "end_at": 1.0, "weight_type": "standard"}}
                final_model = [str(nid), 0]; nid += 1

        # Encode
        nodes[str(nid)] = {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": clip_conn}}
        neg_node = str(nid); nid += 1
        nodes[str(nid)] = {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": clip_conn}}
        pos_node = str(nid); nid += 1

        # Latent
        nodes[str(nid)] = {"class_type": "EmptyLatentImage",
                           "inputs": {"width": w, "height": H, "batch_size": 1}}
        latent_node = str(nid); nid += 1

        # KSampler
        nodes[str(nid)] = {"class_type": "KSampler",
                           "inputs": {
                               "seed": seed, "steps": steps, "cfg": cfg,
                               "sampler_name": DEFAULT_SAMPLER, "scheduler": DEFAULT_SCHEDULER,
                               "denoise": 1.0,
                               "model": final_model, "positive": [pos_node, 0],
                               "negative": [neg_node, 0], "latent_image": [latent_node, 0]}}
        sampler_node = str(nid); nid += 1

        # VAE Decode
        nodes[str(nid)] = {"class_type": "VAEDecode",
                           "inputs": {"samples": [sampler_node, 0], "vae": ["1", 2]}}
        decode_node = str(nid); nid += 1

        # Save
        nodes[str(nid)] = {"class_type": "SaveImage",
                           "inputs": {"filename_prefix": prefix, "images": [decode_node, 0]}}

        return nodes

    def _upload_ref(self, path):
        if not path or not os.path.exists(path):
            return None
        url = f"http://{self.host_var.get()}:{self.port_var.get()}/upload/image"
        fname = os.path.basename(path)
        try:
            with open(path, "rb") as f:
                r = requests.post(url, files={"image": (fname, f, "image/png")}, timeout=30)
            r.raise_for_status()
            return r.json()["name"]
        except Exception as e:
            self.log(f"参照画像アップロード失敗: {e}")
            return None

    def _gen_one(self, wf, prefix, out_dir):
        url = f"http://{self.host_var.get()}:{self.port_var.get()}/prompt"
        try:
            r = requests.post(url, json={"prompt": wf}, timeout=30)
            r.raise_for_status()
            pid = r.json()["prompt_id"]
        except Exception as e:
            self.log(f"  {prefix} SUBMIT: {e}")
            return
        for j in range(150):
            if not self.generating:
                return
            time.sleep(2)
            try:
                h = requests.get(f"{url.replace('/prompt','/history')}/{pid}", timeout=10).json()
                if pid in h:
                    st = h[pid]["status"]["status_str"]
                    if st == "success":
                        for nid, node in h[pid]["outputs"].items():
                            for img in node.get("images", []):
                                params = urllib.parse.urlencode({
                                    "filename": img["filename"], "subfolder": img["subfolder"],
                                    "type": img["type"]})
                                dl_url = f"{url.replace('/prompt','/view')}?{params}"
                                outpath = os.path.join(out_dir, img["filename"])
                                resp = requests.get(dl_url, timeout=60)
                                if len(resp.content) > 1000:
                                    with open(outpath, "wb") as f:
                                        f.write(resp.content)
                                    self.log(f"  {prefix} OK ({len(resp.content)//1024}kb)")
                                else:
                                    self.log(f"  {prefix} EMPTY ({len(resp.content)}b)")
                        return
                    elif st == "error":
                        err = h[pid]["status"].get("messages", [["", {}]])[-1][1].get("exception_message", "unknown")
                        self.log(f"  {prefix} ERROR: {err}")
                        return
            except:
                if j == 149:
                    self.log(f"  {prefix} TIMEOUT")


if __name__ == "__main__":
    root = tk.Tk()
    app = ComfyUIGUI(root)
    root.mainloop()
