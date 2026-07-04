"""
ComfyUI 画像生成ツール v3 — NSFWカテゴリ選択対応
作者: AINovel pipeline
使い方: novels/生成/comfyui_gen_tool_README.md 参照

M1 Mac Mini ComfyUI API (yayoi_mix SD1.5) に接続して画像生成。
ランダムプロンプト生成 + SFW/NSFW切替 + NSFWカテゴリ選択対応。
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests, json, time, os, threading, urllib.parse, random

DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
HOST = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1 = "JapaneseDollLikeness_v15.safetensors"
LORA2 = "DetailTweaker.safetensors"

DEFAULT_NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
               "cartoon, anime, illustration, painting, 3d render, cgi, "
               "oversaturated, hdr, plastic skin, airbrushed, "
               "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
               "watermark, signature, text, logo, existing celebrity, real person, copyrighted character"
               ", male, man, boy, 1boy, young man, old man")

def age_to_desc(age):
    if age <= 12:  return f"{age} year old japanese girl, elementary school student"
    if age <= 15:  return f"{age} year old japanese girl, middle school student"
    if age <= 18:  return f"{age} year old japanese young woman, high school student"
    if age <= 22:  return f"{age} year old japanese young woman, university student"
    if age <= 30:  return f"{age} year old japanese woman, office worker"
    return f"{age} year old japanese woman"

HAIR = ["long straight black hair, neat bangs",
        "long straight black hair, loose, hair behind ears",
        "long straight black hair tied in low ponytail",
        "long straight black hair, messy bun on top",
        "short black bob haircut, neat straight bangs",
        "shoulder length black hair, soft waves",
        "long straight black hair, twin tails",
        "short black hair, natural side part"]

CLOTHES_UNIFORM = ["navy blazer, white blouse, gray pleated skirt, navy ribbon",
                   "navy blazer, white blouse, gray pleated skirt, red ribbon",
                   "white button shirt, gray vest, pleated skirt",
                   "sailor uniform, white collar, navy skirt",
                   "blazer, knitted vest, white shirt, striped tie"]

CLOTHES_CASUAL = ["plain white t-shirt, light blue denim jacket",
                  "oversized cream knit sweater",
                  "gray zip-up hoodie, plain t-shirt underneath",
                  "beige cardigan, white blouse, brown skirt",
                  "denim jacket, white t-shirt, denim shorts",
                  "striped long sleeve t-shirt, denim skirt",
                  "black oversized hoodie, gray sweatpants",
                  "white t-shirt, jeans, canvas sneakers",
                  "track jacket, black leggings, sneakers",
                  "simple cotton t-shirt, comfortable pants"]

CLOTHES_FORMAL = ["navy suit, white shirt, dark red tie",
                  "gray suit, white shirt, blue tie",
                  "white shirt, navy vest, no jacket",
                  "navy overcoat, scarf, suit underneath"]

EXPRESSION = ["shy expression",
              "slight smile",
              "serious face, focused",
              "thoughtful look, looking away",
              "tired, worn out",
              "calm, relaxed",
              "sad, lonely",
              "determined look",
              "surprised, eyes wide",
              "neutral expression"]

EXPRESSION_NSFW = EXPRESSION + ["lustful gaze", "ahegao expression", "seductive smile",
                                 "teary eyes, blushing", "biting lip, lustful"]

SCENE = ["school entrance, morning",
         "classroom, afternoon light",
         "school corridor, window light",
         "library, quiet atmosphere",
         "courtyard, sunny day",
         "cafe, warm interior",
         "park, afternoon",
         "home, living room",
         "street, evening",
         "office, desk",
         "bookstore",
         "stairwell, quiet"]

SCENE_NSFW = SCENE + ["bedroom, dim lighting", "love hotel room", "bathroom, mirror",
                       "shower, wet", "dressing room, mirror"]

# ポーズ一覧: (表示ラベル, プロンプト文字列)
POSE_OPTIONS = [
    ("正面立ち", "front view, standing, facing camera"),
    ("斜め立ち", "three-quarter view, standing, looking slightly to the side"),
    ("横向き", "side view, profile"),
    ("椅子座り", "front view, sitting, hands on lap"),
    ("机座り", "three-quarter view, sitting at desk"),
    ("窓辺立ち", "front view, standing by window, natural light"),
    ("歩き", "three-quarter view, walking, looking ahead"),
    ("廊下横", "side view, walking down corridor"),
    ("ソファ座り", "front view, sitting on sofa, relaxed"),
    ("壁もたれ", "three-quarter view, leaning against wall"),
    ("手ポケット", "front view, standing, hands in pocket"),
    ("ベンチ座り", "sitting on park bench, afternoon"),
    ("ベッド寝転び", "lying on bed, looking up"),
    ("四つん這い", "on hands and knees, looking back"),
    ("ベッド腰掛け", "sitting on edge of bed, legs slightly apart"),
    ("前かがみ", "standing, leaning forward, hands on knees"),
    ("開脚椅子", "spread legs, sitting on chair, looking at camera"),
    ("仰向け開脚", "on back, legs raised"),
    ("跪き", "kneeling, looking up"),
]

NSFW_CATEGORIES = {
    "まんこ/ヴァギナ":    ["pussy", "spread pussy", "vagina", "open pussy", "pussy juice", "no clothes"],
    "おっぱい(breasts)":  ["big breasts", "breasts exposed", "cleavage", "nipples", "bare breasts", "medium breasts", "small breasts"],
    "下着(lingerie)":     ["lingerie", "lace bra", "panties", "stockings", "garter belt", "babydoll", "thighhighs"],
    "トップレス":         ["topless", "no bra", "bare chest", "exposed breasts", "no shirt"],
    "パンチラ":           ["upskirt", "panty shot", "visible panties", "skirt lifted", "from below angle"],
    "ブラチラ":           ["bra visible", "bra strap visible", "sheer blouse", "see-through top", "bra outline"],
    "尻(ass)":           ["ass", "butt", "round ass", "spread ass"],
    "陰毛(pubic hair)":   ["pubic hair", "visible pubic hair", "shaved", "trimmed", "landing strip"],
    "断面図(close up)":   ["close up", "spread legs", "naked"],
    "中出し(cum)":        ["cum", "cum inside", "creampie", "cum on body", "semen"],
}


class ComfyApp:
    def __init__(self, root):
        self.root = root
        root.title("ComfyUI 画像生成")
        root.geometry("720x1020")
        root.resizable(True, True)
        self.generating = False
        self._nsfw_override = None
        self.sfw_mode = tk.IntVar(value=2)

        main = ttk.Frame(root, padding=10)
        main.pack(fill="both", expand=True)

        # ─── ランダム生成 ───
        rand_frame = ttk.LabelFrame(main, text="プロンプト自動作成", padding=5)
        rand_frame.pack(fill="x", pady=(0,5))

        ttk.Button(rand_frame, text="ランダム生成",
                   command=self.random_prompt).pack(side="left", padx=2)

        self.mode_var = tk.StringVar(value="制服")
        ttk.Radiobutton(rand_frame, text="制服", variable=self.mode_var,
                        value="制服").pack(side="left", padx=5)
        ttk.Radiobutton(rand_frame, text="私服", variable=self.mode_var,
                        value="私服").pack(side="left", padx=5)
        ttk.Radiobutton(rand_frame, text="スーツ", variable=self.mode_var,
                        value="スーツ").pack(side="left", padx=5)

        sep = ttk.Separator(rand_frame, orient="vertical")
        sep.pack(side="left", fill="y", padx=10)

        ttk.Radiobutton(rand_frame, text="ランダム", variable=self.sfw_mode,
                        value=2).pack(side="left", padx=2)
        ttk.Radiobutton(rand_frame, text="SFW", variable=self.sfw_mode,
                        value=1).pack(side="left", padx=2)
        ttk.Radiobutton(rand_frame, text="NSFW", variable=self.sfw_mode,
                        value=0).pack(side="left", padx=2)

        # ─── NSFWカテゴリ選択（常時表示、SFW時のみdisable） ───
        self.nsfw_cat_frame = ttk.LabelFrame(main, text="NSFWカテゴリ（ONにしたものをランダム時追加）", padding=5)
        self.nsfw_cat_vars = {}
        self.nsfw_cat_cbs = []
        cat_row = ttk.Frame(self.nsfw_cat_frame)
        cat_row.pack(fill="x")
        for i, (label, _) in enumerate(NSFW_CATEGORIES.items()):
            v = tk.IntVar(value=0)
            self.nsfw_cat_vars[label] = v
            cb = ttk.Checkbutton(cat_row, text=label, variable=v)
            cb.grid(row=i // 5, column=i % 5, sticky="w", padx=3, pady=1)
            self.nsfw_cat_cbs.append(cb)
        self.nsfw_cat_frame.pack(fill="x", pady=(0,5))

        # ─── 年齢 ───
        age_frame = ttk.Frame(main)
        age_frame.pack(fill="x", pady=(0,5))
        ttk.Label(age_frame, text="年齢:").pack(side="left")
        self.age_var = tk.IntVar(value=14)
        ttk.Spinbox(age_frame, from_=10, to=50, increment=1, textvariable=self.age_var, width=4).pack(side="left", padx=2)
        self.age_label = ttk.Label(age_frame, text=age_to_desc(14), foreground="#888")
        self.age_label.pack(side="left", padx=5)
        self.age_var.trace_add("write", self._update_age_label)

        # ─── ポーズ選択（単一選択） ───
        pose_frame = ttk.LabelFrame(main, text="ポーズ選択", padding=5)
        self.pose_var = tk.StringVar(value="ランダム")
        poses = [("ランダム", "ランダム")] + POSE_OPTIONS
        pose_grid = ttk.Frame(pose_frame)
        pose_grid.pack(fill="x")
        for i, (label, _) in enumerate(poses):
            ttk.Radiobutton(pose_grid, text=label, variable=self.pose_var,
                            value=label).grid(row=i // 4, column=i % 4, sticky="w", padx=3, pady=1)
        pose_frame.pack(fill="x", pady=(0,5))

        # ─── プロンプト入力 ───
        ttk.Label(main, text="プロンプト:").pack(anchor="w")
        self.prompt_text = tk.Text(main, height=8, wrap="word", font=("メイリオ", 10))
        self.prompt_text.pack(fill="x", pady=2)

        ttk.Label(main, text="ネガティブプロンプト:").pack(anchor="w", pady=(8,0))
        self.neg_text = tk.Text(main, height=3, wrap="word", font=("メイリオ", 9))
        self.neg_text.pack(fill="x", pady=2)
        self.neg_text.insert("1.0", DEFAULT_NEG)

        # ─── 生成設定 ───
        cf = ttk.Frame(main)
        cf.pack(fill="x", pady=8)

        ttk.Label(cf, text="Seed:").pack(side="left")
        self.seed_var = tk.StringVar(value="random")
        ttk.Entry(cf, textvariable=self.seed_var, width=14).pack(side="left", padx=2)
        ttk.Label(cf, text="  CFG:").pack(side="left", padx=(8,0))
        self.cfg_var = tk.StringVar(value="7.0")
        ttk.Spinbox(cf, from_=1, to=20, increment=0.5, textvariable=self.cfg_var, width=5).pack(side="left", padx=2)
        ttk.Label(cf, text="  Steps:").pack(side="left", padx=(8,0))
        self.steps_var = tk.StringVar(value="28")
        ttk.Spinbox(cf, from_=10, to=60, increment=1, textvariable=self.steps_var, width=5).pack(side="left", padx=2)
        ttk.Label(cf, text="  枚数:").pack(side="left", padx=(8,0))
        self.count_var = tk.IntVar(value=1)
        ttk.Spinbox(cf, from_=1, to=20, increment=1, textvariable=self.count_var, width=4).pack(side="left", padx=2)


        # ─── 生成/停止 ───
        self.go_btn = tk.Button(main, text="生 成", font=("メイリオ", 16, "bold"),
                                bg="#4CAF50", fg="white", height=2,
                                command=self.start_gen)
        self.go_btn.pack(fill="x", pady=8)

        self.progress = ttk.Progressbar(main, mode="indeterminate")
        self.progress.pack(fill="x")
        self.status_var = tk.StringVar(value="待機中")
        ttk.Label(main, textvariable=self.status_var, foreground="#666").pack(anchor="w")

        # ─── ログ ───
        ttk.Label(main, text="ログ:").pack(anchor="w")
        self.log_text = scrolledtext.ScrolledText(main, height=8, state="disabled",
                                                    wrap="word", font=("メイリオ", 9))
        self.log_text.pack(fill="both", expand=True, pady=2)

        # SFW/NSFW切替でカテゴリ枠の表示を切替
        self.sfw_mode.trace_add("write", self._toggle_nsfw_cats)

    def _update_age_label(self, *_):
        self.age_label.configure(text=age_to_desc(self.age_var.get()))

    def _toggle_nsfw_cats(self, *_):
        enabled = (self.sfw_mode.get() != 1)
        for cb in self.nsfw_cat_cbs:
            cb.configure(state="normal" if enabled else "disabled")
        self.nsfw_cat_frame.configure(text="NSFWカテゴリ"
                                      if enabled else "NSFWカテゴリ（SFW時は無効）")

    def random_prompt(self):
        """ランダムプロンプトを生成してテキストエリアにセット"""
        rdmode = self.sfw_mode.get()
        if rdmode == 2:
            nsfw = random.choice([True, False])
            self._nsfw_override = nsfw
        else:
            nsfw = (rdmode == 0)
            self._nsfw_override = None
        char = age_to_desc(self.age_var.get())
        hair = random.choice(HAIR)
        expr_list = EXPRESSION_NSFW if nsfw else EXPRESSION
        scene_list = SCENE_NSFW if nsfw else SCENE
        expr = random.choice(expr_list)
        scene = random.choice(scene_list)

        selected = self.pose_var.get()
        if selected == "ランダム":
            idx = random.randrange(len(POSE_OPTIONS))
        else:
            idx = [i for i, (label, _) in enumerate(POSE_OPTIONS) if label == selected][0]
        pose = POSE_OPTIONS[idx][1]

        mode = self.mode_var.get()
        if nsfw:
            clothes = ""
        else:
            if mode == "制服":
                clothes_list = CLOTHES_UNIFORM
            elif mode == "私服":
                clothes_list = CLOTHES_CASUAL
            else:
                clothes_list = CLOTHES_FORMAL
            clothes = random.choice(clothes_list)

        # NSFWカテゴリキーワード（先に構築。服装の前に配置するため）
        nsfw_part = ""
        cats_on = []
        if nsfw:
            extra_tags = ["naked", "nude"]
            for label, keywords in NSFW_CATEGORIES.items():
                if self.nsfw_cat_vars.get(label, tk.IntVar(value=0)).get() == 1:
                    picked = random.choice(keywords)
                    extra_tags.append(picked)
                    cats_on.append(label)
            if not cats_on:
                # 未チェック＝全カテゴリからランダム
                picked_labels = random.sample(list(NSFW_CATEGORIES.keys()), random.randint(1, 2))
                for lbl in picked_labels:
                    extra_tags.append(random.choice(NSFW_CATEGORIES[lbl]))
                    cats_on.append(lbl)
            nsfw_part = ", " + ", ".join(extra_tags)

        gender_tag = "1girl, female, solo"
        clothes_part = f", {clothes}" if clothes else ""
        base = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
                f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
                f"{gender_tag}, {char}, {hair}{nsfw_part}{clothes_part}, {pose}, {expr}, {scene}")

        self.prompt_text.delete("1.0", "end")
        self.prompt_text.insert("1.0", base)
        cat_str = f" / カテゴリ:{','.join(cats_on)}" if cats_on else ""
        pose_label = POSE_OPTIONS[idx][0]
        self.log(f"ランダム生成: {'NSFW' if nsfw else 'SFW'} / {mode} / {pose_label}{cat_str}")
        self.log(f"  → FULL: {base}")

        # ネガティブ自動切替
        neg = self.neg_text.get("1.0", "end-1c")
        if nsfw:
            if "nude, exposed" in neg:
                new_neg = neg.replace(", nude, exposed", "").replace("nude, exposed, ", "")
                self.neg_text.delete("1.0", "end")
                self.neg_text.insert("1.0", new_neg)
                self.log("  ネガティブ: nude/exposed 除去")
        else:
            if "nude, exposed" not in neg:
                self.neg_text.delete("1.0", "end")
                self.neg_text.insert("1.0", neg + ", nude, exposed")
                self.log("  ネガティブ: nude/exposed 追加")

    def log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
        self.root.update_idletasks()

    def status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def start_gen(self):
        if self.generating:
            return
        prompt = self.prompt_text.get("1.0", "end-1c").strip()
        if not prompt:
            messagebox.showwarning("警告", "プロンプトを入力してください")
            return
        self.generating = True
        self.go_btn.configure(text="停 止", bg="#f44336", command=self.stop_gen)
        self.progress.start(20)
        threading.Thread(target=self.run, daemon=True).start()

    def stop_gen(self):
        self.generating = False

    def run(self):
        prompt = self.prompt_text.get("1.0", "end-1c").strip()
        neg = self.neg_text.get("1.0", "end-1c").strip()
        count = self.count_var.get()
        cfg = float(self.cfg_var.get())
        steps = int(self.steps_var.get())
        seed_str = self.seed_var.get().strip().lower()
        nsfw = self._nsfw_override if self._nsfw_override is not None else (self.sfw_mode.get() == 0)
        self._nsfw_override = None

        self.log(f"生成開始: {count}枚")
        self.status(f"生成中 (0/{count})")

        for i in range(count):
            if not self.generating:
                self.log("停止されました")
                break
            seed = self._get_seed(seed_str)
            prefix = f"gen_{time.strftime('%m%d_%H%M%S')}_s{seed}"
            self.log(f"[{i+1}/{count}] seed={seed} 送信中...")
            self.status(f"生成中 ({i+1}/{count})")
            wf = self._build_wf(prompt, neg, seed, cfg, steps, prefix, nsfw)
            ok = self._send_and_save(wf, prefix)
            self.log(f"  {'OK' if ok else '失敗'}")
            time.sleep(0.3)

        self.generating = False
        self.go_btn.configure(text="生 成", bg="#4CAF50", command=self.start_gen)
        self.progress.stop()
        self.progress["value"] = 0
        self.status("完了")

    def _get_seed(self, s):
        if s == "random":
            return random.randint(1000000000, 9999999999)
        try:
            return int(s)
        except:
            return random.randint(1000000000, 9999999999)

    def _build_wf(self, prompt, neg, seed, cfg, steps, prefix, nsfw=False):
        doll_s = 0.1 if nsfw else 0.5
        return {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
            "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0],"clip":["1",1],"lora_name":LORA1,"strength_model":doll_s,"strength_clip":doll_s}},
            "3": {"class_type": "LoraLoader", "inputs": {"model":["2",0],"clip":["2",1],"lora_name":LORA2,"strength_model":0.2,"strength_clip":0.2}},
            "4": {"class_type": "CLIPTextEncode", "inputs": {"text":neg,"clip":["3",1]}},
            "5": {"class_type": "CLIPTextEncode", "inputs": {"text":prompt,"clip":["3",1]}},
            "6": {"class_type": "EmptyLatentImage", "inputs": {"width":512,"height":768,"batch_size":1}},
            "7": {"class_type": "KSampler", "inputs":{"seed":seed,"steps":steps,"cfg":cfg,"sampler_name":"dpmpp_2m","scheduler":"karras","denoise":1.0,"model":["3",0],"positive":["5",0],"negative":["4",0],"latent_image":["6",0]}},
            "8": {"class_type": "VAEDecode", "inputs": {"samples":["7",0],"vae":["1",2]}},
            "9": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix,"images":["8",0]}},
        }

    def _send_and_save(self, wf, prefix):
        try:
            r = requests.post(f"{HOST}/prompt", json={"prompt":wf}, timeout=30)
            r.raise_for_status()
            pid = r.json()["prompt_id"]
        except Exception as e:
            self.log(f"  送信失敗: {e}")
            return False
        for j in range(150):
            if not self.generating:
                return False
            time.sleep(1.5)
            try:
                h = requests.get(f"{HOST}/history/{pid}", timeout=10).json()
                if pid in h:
                    st = h[pid]["status"]["status_str"]
                    if st == "success":
                        outdir = os.path.join(DESKTOP, "output")
                        os.makedirs(outdir, exist_ok=True)
                        for nid, node in h[pid]["outputs"].items():
                            for img in node.get("images", []):
                                params = urllib.parse.urlencode({"filename":img["filename"],"subfolder":img["subfolder"],"type":img["type"]})
                                url = f"{HOST}/view?{params}"
                                resp = requests.get(url, timeout=60)
                                if len(resp.content) > 1000:
                                    with open(os.path.join(outdir, img["filename"]), "wb") as f: f.write(resp.content)
                        return True
                    elif st == "error":
                        err = h[pid]["status"].get("messages",[[ "",{}]])[-1][1].get("exception_message","unknown")
                        self.log(f"  ERROR: {err}")
                        return False
            except:
                continue
        self.log("  TIMEOUT")
        return False

if __name__ == "__main__":
    root = tk.Tk()
    app = ComfyApp(root)
    root.mainloop()
