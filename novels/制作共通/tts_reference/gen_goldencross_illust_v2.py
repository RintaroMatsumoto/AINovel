"""GoldenCross 挿絵 v2 — 全キャラ顔一致
手法: 
  - 単体キャラ: FaceID/IPAdapter txt2img (従来通り)
  - 複数キャラ: txt2img構図 → img2img + FaceID 逐次リファイン (denoise 0.55)
"""
import requests, json, time, os, sys, random, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
W, H, STEPS = 512, 768, 28
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT_PRO = r"C:\Users\GoldRush\Documents\MyProject\AIvideo\_素材\goldencross_illust\プロローグ"
OUT_C1  = r"C:\Users\GoldRush\Documents\MyProject\AIvideo\_素材\goldencross_illust\第1章"
os.makedirs(OUT_PRO, exist_ok=True)
os.makedirs(OUT_C1, exist_ok=True)

# === 参照画像 ===
BASE_DIR = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像"
REFS = {
    "makoto40": os.path.join(BASE_DIR, r"橘誠\02_40歳_退職前\採用\makoto_40_yayoi_mix_fid4_cfg9_s6250727949_cafe_street_00001_.png"),
    "yuriko34": os.path.join(BASE_DIR, r"橘百合子\02_18歳_回想_新入社員\yuriko_face_s5977_00001_.png"),
    "shiori14": os.path.join(BASE_DIR, r"橘栞\01_14歳_中学生\採用\shiori_13_yayoi_mix_s1193774_casual_hoodie_front_00002_.png"),
    "shiori3":  os.path.join(BASE_DIR, r"橘栞\01_14歳_中学生\採用\shiori_13_yayoi_mix_s1193774_casual_hoodie_front_00002_.png"),
    "tsubasa11":os.path.join(BASE_DIR, r"橘翼\02_11歳_小学生\採用\tsubasa_11_yurikos5977_07_00001_.png"),
    "bucho":    os.path.join(BASE_DIR, r"部長\01_55歳_経理部長\採用\bucho_majic_v2_cfg8.0_s889003312_01_00001_.png"),
    "oba":      os.path.join(BASE_DIR, r"叔母\01_60代_札幌\採用\oba_majic_v4_cfg8.0_s876174573_03_00001_.png"),
}

# === アップロード済み参照名を保持 ===
UPLOADED = {}

def img_name(key):
    return f"ref_{key}.png"

def upload_all():
    for key, path in REFS.items():
        if not os.path.exists(path):
            print(f"  WARN: ref {key} not found: {path}")
            continue
        with open(path, "rb") as f:
            r = requests.post(f"{BASE}/upload/image",
                              files={"image": (img_name(key), f, "image/png")}, timeout=30)
        if r.status_code == 200:
            UPLOADED[key] = img_name(key)
            print(f"  Upload {key}: {r.json()['name']}")
        else:
            print(f"  Upload {key} FAILED: {r.status_code}")
        time.sleep(0.2)

# === ネガティブ ===
NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person")

NEG_MALE = NEG + (", feminine, woman, female features, effeminate, "
                   "androgynous, soft face, delicate, pretty, girly, "
                   "curly hair, wavy hair, "
                   "pompadour, quiff, slicked back, excessive volume, "
                   "host style, flashy hair, gel hair, spiky hair")

NEG_CHILD = NEG + (", adult, mature, old, aging, wrinkles, "
                    "heavy makeup, lipstick, dyed hair, "
                    "colored hair, curly hair, wavy hair")

NEG_YURIKO = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
              "cartoon, anime, illustration, painting, 3d render, cgi, "
              "nude, exposed, oversaturated, hdr, airbrushed, "
              "mutated hands, extra fingers, deformed, bad anatomy, "
              "watermark, signature, text, logo, existing celebrity, real person, "
              "makeup, frills, lace, ribbon, curly hair, wavy hair, "
              "bangs, bob cut, shoulder-length, "
              "young, teen, adolescent, childish, "
              "cute, kawaii, innocent, glowing skin, radiant, fresh-faced")

PB = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
      "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed")
PB_MALE = (f"{PB}, japanese man, 40 years old, salaryman, "
           "masculine face, strong jawline, clean shaven, "
           "natural salt and pepper hair, neatly combed side part, "
           "silver thin metal frame glasses, "
           "tired eyes, weary gaze, dark circles, subdued expression")
PB_YURIKO = (f"{PB}, 34-years-old, mature woman, thirties, "
             "long straight black hair, plain natural face, no makeup, "
             "mother of two, experienced tired gaze, "
             "distant thoughtful expression, quiet weariness")
PB_SHIORI14 = (f"{PB}, 14 year old japanese girl, "
               "long straight black hair, cute innocent face, "
               "bright intelligent eyes, slender, private school style")
PB_SHIORI3 = (f"{PB}, 3 year old japanese toddler girl, "
              "long straight black hair, cute innocent face, "
              "chubby cheeks, big curious eyes, lovely child smile")
PB_TSUBASA11 = (f"{PB}, 11 year old japanese boy, "
                "short black hair, small thin build, "
                "innocent smile, happy child")

# ============================================================
# 汎用 submit + download
# ============================================================
def submit_and_save(wf, outdir, prefix, timeout_sec=600):
    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt": wf}, timeout=30)
        r.raise_for_status()
        pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  [{prefix}] SUBMIT: {e}")
        return None
    for j in range(timeout_sec // 2):
        time.sleep(2)
        try:
            h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
            if pid in h:
                st = h[pid]["status"]["status_str"]
                if st == "success":
                    saved = []
                    for nid, node in h[pid]["outputs"].items():
                        for img in node.get("images", []):
                            params = urllib.parse.urlencode({
                                "filename": img["filename"], "subfolder": img["subfolder"], "type": img["type"]
                            })
                            url = f"{BASE}/view?{params}"
                            outpath = os.path.join(outdir, img["filename"])
                            resp = requests.get(url, timeout=60)
                            if len(resp.content) > 1000:
                                with open(outpath, "wb") as f: f.write(resp.content)
                                saved.append(outpath)
                                print(f"    {img['filename']} ({len(resp.content)//1024}kb)")
                            else:
                                print(f"    EMPTY ({len(resp.content)}b)")
                    return saved[-1] if saved else None
                elif st == "error":
                    print(f"  [{prefix}] ERROR"); return None
        except:
            if j == (timeout_sec // 2 - 1):
                print(f"  [{prefix}] TIMEOUT")
                return None
    return None

# ============================================================
# 方式A: IPAdapter-only txt2img (誠40用)
# ============================================================
def gen_makoto40(tag, extra_prompt, outdir, seed=None):
    if seed is None:
        seed = random.randint(1000000000, 9999999999)
    ref_name = UPLOADED.get("makoto40")
    if not ref_name:
        print(f"  [{tag}] SKIP: no makoto40 ref"); return None
    prefix = f"m40_{tag}_s{seed}"
    print(f"[{prefix}]")
    prompt = f"{PB_MALE}, {extra_prompt}"
    esc_p = prompt.replace('"', '\\"')
    esc_n = NEG_MALE.replace('"', '\\"')
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "IPAdapterUnifiedLoader", "inputs": {"model":["1",0], "preset":"STANDARD (medium strength)"}},
        "3": {"class_type": "LoadImage", "inputs": {"image": ref_name}},
        "4": {"class_type": "IPAdapter", "inputs": {"model":["2",0], "ipadapter":["2",1], "image":["3",0], "weight":0.45, "start_at":0.0, "end_at":1.0, "weight_type":"standard"}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": esc_n, "clip":["1",1]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": esc_p, "clip":["1",1]}},
        "7": {"class_type": "EmptyLatentImage", "inputs": {"width":W, "height":H, "batch_size":1}},
        "8": {"class_type": "KSampler", "inputs": {"seed":seed, "steps":STEPS, "cfg":7.5, "sampler_name":SAMPLER, "scheduler":SCHEDULER, "denoise":1.0, "model":["4",0], "positive":["6",0], "negative":["5",0], "latent_image":["7",0]}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples":["8",0], "vae":["1",2]}},
        "10": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix, "images":["9",0]}},
    }
    return submit_and_save(wf, outdir, prefix)

# ============================================================
# 方式B: FaceID txt2img (単体キャラ)
# ============================================================
def gen_faceid(tag, ref_key, prompt, outdir, params, seed=None):
    if seed is None:
        seed = random.randint(1000000000, 9999999999)
    ref_name = UPLOADED.get(ref_key)
    if not ref_name:
        print(f"  [{tag}] SKIP: no {ref_key} ref"); return None
    prefix = f"fid_{tag}_s{seed}"
    print(f"[{prefix}]")

    fw = params.get("fw", 0.8)
    cfg = params.get("cfg", 7.0)
    doll = params.get("doll", 0.5)
    dt = params.get("dt", 0.2)
    neg = params.get("neg", NEG)

    esc_p = prompt.replace('"', '\\"')
    esc_n = neg.replace('"', '\\"')

    wf = {"1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}}}
    md = "1"
    if doll > 0:
        wf["1a"] = {"class_type": "LoraLoader", "inputs": {"model":["1",0], "clip":["1",1],
            "lora_name":"JapaneseDollLikeness_v15.safetensors", "strength_model":doll, "strength_clip":doll}}
        md = "1a"
    if dt > 0:
        wf["1b"] = {"class_type": "LoraLoader", "inputs": {"model":[md,0], "clip":[md,1],
            "lora_name":"DetailTweaker.safetensors", "strength_model":dt, "strength_clip":dt}}
        md = "1b"

    wf["2"] = {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":[md,0], "preset":"FACEID PLUS V2", "lora_strength":0.5, "provider":"CPU"}}
    wf["3"] = {"class_type": "LoadImage", "inputs": {"image": ref_name}}
    wf["4"] = {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU", "model_name":"buffalo_l"}}
    wf["5"] = {"class_type": "IPAdapterFaceID", "inputs": {
        "model":["2",0], "ipadapter":["2",1], "image":["3",0],
        "weight":fw, "weight_faceidv2":0.0,
        "weight_type":"linear", "combine_embeds":"concat",
        "start_at":0.0, "end_at":1.0, "embeds_scaling":"V only",
        "insightface":["4",0]
    }}
    wf["6"] = {"class_type": "CLIPTextEncode", "inputs": {"text": esc_n, "clip":[md,1]}}
    wf["7"] = {"class_type": "CLIPTextEncode", "inputs": {"text": esc_p, "clip":[md,1]}}
    wf["8"] = {"class_type": "EmptyLatentImage", "inputs": {"width":W, "height":H, "batch_size":1}}
    wf["9"] = {"class_type": "KSampler", "inputs": {
        "seed":seed, "steps":STEPS, "cfg":cfg,
        "sampler_name":SAMPLER, "scheduler":SCHEDULER, "denoise":1.0,
        "model":["5",0], "positive":["7",0], "negative":["6",0], "latent_image":["8",0]
    }}
    wf["10"] = {"class_type": "VAEDecode", "inputs": {"samples":["9",0], "vae":["1",2]}}
    wf["11"] = {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix, "images":["10",0]}}
    return submit_and_save(wf, outdir, prefix)

# ============================================================
# 方式C: 複数キャラ — txt2img構図 → img2img + FaceID 逐次リファイン
# ============================================================
def gen_multichar(tag, base_prompt, outdir,
                  refine_steps=None, neg=None, seed=None, cfg=7.5):
    """refine_steps: [(ref_key, params), ...] — 順次FaceIDリファイン"""
    if seed is None:
        seed = random.randint(1000000000, 9999999999)
    prefix = f"multi_{tag}_s{seed}"
    print(f"[{prefix}]")
    neg = neg or NEG

    # Step 1: txt2img 構図生成 (LoRAあり)
    esc_p = base_prompt.replace('"', '\\"')
    esc_n = neg.replace('"', '\\"')
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0], "clip":["1",1], "lora_name":"JapaneseDollLikeness_v15.safetensors", "strength_model":0.5, "strength_clip":0.5}},
        "3": {"class_type": "LoraLoader", "inputs": {"model":["2",0], "clip":["2",1], "lora_name":"DetailTweaker.safetensors", "strength_model":0.2, "strength_clip":0.2}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": esc_n, "clip":["3",1]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": esc_p, "clip":["3",1]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width":W, "height":H, "batch_size":1}},
        "7": {"class_type": "KSampler", "inputs": {"seed":seed, "steps":STEPS, "cfg":cfg, "sampler_name":SAMPLER, "scheduler":SCHEDULER, "denoise":1.0, "model":["3",0], "positive":["5",0], "negative":["4",0], "latent_image":["6",0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples":["7",0], "vae":["1",2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix":f"{prefix}_base", "images":["8",0]}},
    }
    result_path = submit_and_save(wf, outdir, f"{prefix}_base")
    if not result_path:
        print(f"  [{prefix}] base gen failed")
        return None

    # Step 2-N: img2img で各キャラの顔を順次リファイン
    current_path = result_path
    for i, (ref_key, rparams) in enumerate(refine_steps or []):
        ref_name = UPLOADED.get(ref_key)
        if not ref_name:
            print(f"  [{prefix}] SKIP refine {ref_key}: no ref"); continue

        step_tag = f"{prefix}_r{i+1}"
        fw = rparams.get("fw", 0.8)
        r_cfg = rparams.get("cfg", 7.0)
        denoise = rparams.get("denoise", 0.55)
        doll_r = rparams.get("doll", 0.0)
        dt_r = rparams.get("dt", 0.0)
        refine_neg = rparams.get("neg", NEG)
        char_prompt_extra = rparams.get("prompt", "")

        print(f"  refine[{i+1}] {ref_key} (fw={fw}, denoise={denoise})")

        # Load current image (the result from previous step)
        # Need to read it from disk and upload as a temp image for LoadImage
        with open(current_path, "rb") as f:
            r = requests.post(f"{BASE}/upload/image",
                              files={"image": (f"current_{tag}_{i}.png", f, "image/png")}, timeout=30)
        if r.status_code != 200:
            print(f"    upload current FAILED"); continue
        current_ref = r.json()["name"]

        # Build img2img + FaceID workflow
        wf_r = {"1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}}}
        md_r = "1"
        if doll_r > 0:
            wf_r["1a"] = {"class_type": "LoraLoader", "inputs": {"model":["1",0], "clip":["1",1],
                "lora_name":"JapaneseDollLikeness_v15.safetensors", "strength_model":doll_r, "strength_clip":doll_r}}
            md_r = "1a"
        if dt_r > 0:
            wf_r["1b"] = {"class_type": "LoraLoader", "inputs": {"model":[md_r,0], "clip":[md_r,1],
                "lora_name":"DetailTweaker.safetensors", "strength_model":dt_r, "strength_clip":dt_r}}
            md_r = "1b"

        # Load current image → VAEEncode
        wf_r["10"] = {"class_type": "LoadImage", "inputs": {"image": current_ref}}
        wf_r["11"] = {"class_type": "VAEEncode", "inputs": {"pixels":["10",0], "vae":["1",2]}}

        # FaceID
        wf_r["2"] = {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":[md_r,0], "preset":"FACEID PLUS V2", "lora_strength":0.5, "provider":"CPU"}}
        wf_r["3"] = {"class_type": "LoadImage", "inputs": {"image": ref_name}}
        wf_r["4"] = {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU", "model_name":"buffalo_l"}}
        wf_r["5"] = {"class_type": "IPAdapterFaceID", "inputs": {
            "model":["2",0], "ipadapter":["2",1], "image":["3",0],
            "weight":fw, "weight_faceidv2":0.0,
            "weight_type":"linear", "combine_embeds":"concat",
            "start_at":0.0, "end_at":1.0, "embeds_scaling":"V only",
            "insightface":["4",0]
        }}

        # CLIP (same prompt as base, but with char_prompt_extra for refinement)
        refine_prompt = base_prompt
        if char_prompt_extra:
            refine_prompt = f"{base_prompt}, {char_prompt_extra}"
        esc_pr = refine_prompt.replace('"', '\\"')
        esc_nr = refine_neg.replace('"', '\\"')
        wf_r["6"] = {"class_type": "CLIPTextEncode", "inputs": {"text": esc_nr, "clip":[md_r,1]}}
        wf_r["7"] = {"class_type": "CLIPTextEncode", "inputs": {"text": esc_pr, "clip":[md_r,1]}}

        # KSampler (img2img denoise)
        new_seed = random.randint(1000000000, 9999999999)
        wf_r["8"] = {"class_type": "KSampler", "inputs": {
            "seed":new_seed, "steps":STEPS, "cfg":r_cfg,
            "sampler_name":SAMPLER, "scheduler":SCHEDULER,
            "denoise":denoise,
            "model":["5",0], "positive":["7",0], "negative":["6",0],
            "latent_image":["11",0]  # VAEEncode output
        }}
        wf_r["9"] = {"class_type": "VAEDecode", "inputs": {"samples":["8",0], "vae":["1",2]}}
        wf_r["12"] = {"class_type": "SaveImage", "inputs": {"filename_prefix":step_tag, "images":["9",0]}}

        result_path = submit_and_save(wf_r, outdir, step_tag)
        if not result_path:
            print(f"  [{prefix}] refine {i+1} failed")
            # Continue with previous result anyway

    final_path = result_path or current_path
    # Rename to clean name
    ext = os.path.splitext(final_path)[1]
    clean_name = f"{prefix}{ext}"
    clean_path = os.path.join(outdir, clean_name)
    try:
        os.replace(final_path, clean_path)
        print(f"  => {clean_name}")
    except:
        pass
    return clean_path


# ============================================================
# MAIN
# ============================================================
print("="*50)
print("Phase 1: Upload all reference images")
print("="*50)
upload_all()
print(f"  Uploaded: {list(UPLOADED.keys())}")
time.sleep(1)

# ============================================================
# プロローグ
# ============================================================
print("\n" + "="*50)
print("プロローグ")
print("="*50)

# P1: 書斎の誠 — IPAdapter only (単体)
gen_makoto40("prologue01_study",
    "white shirt, no tie, sleeves slightly rolled, "
    "sitting in office chair, leaning back, looking at dual computer monitors, "
    "stock charts and numbers on screens, green numbers, "
    "home study at night, desk lamp, warm dim light, "
    "content tired expression, slight smile, arms relaxed, "
    "japanese home office, bookshelf in background",
    OUT_PRO)

# P2: キッチンの抱擁 — txt2img → Yuriko FaceID refine
gen_multichar("prologue02_embrace",
    f"{PB}, "
    "japanese couple embracing in kitchen at night, close intimate composition, "
    "34 year old woman with mid-length dark brown hair, "
    "pressing her forehead against man's chest, eyes closed, emotional, "
    "wearing apron over simple navy dress, apron strings visible, "
    "40 year old japanese man in white shirt, holding her, arms around her back, "
    "warm kitchen interior, fluorescent light, "
    "cutting board and half-cut daikon on counter, "
    "intimate tender moment, tears of joy, cinematic photography",
    OUT_PRO,
    refine_steps=[
        ("yuriko34", {"fw":0.3, "cfg":10.0, "doll":0.0, "dt":0.2, "denoise":0.5,
                      "neg": NEG_YURIKO,
                      "prompt": "34 year old woman, mother, pressing face into man's chest"})
    ],
    neg=NEG, cfg=7.5)

# P3: 家族写真 — txt2img → 誠IPAdapter → 百合子FaceID → 栞FaceID → 翼FaceID
gen_multichar("prologue03_family",
    f"{PB}, "
    "japanese family of four at dinner table, flash photography moment, "
    "40 year old father with salt and pepper hair, silver glasses, navy shirt, "
    "34 year old mother with mid-length dark hair, gentle oval face, slight tears in eyes, "
    "14 year old daughter with long straight black hair, school cardigan, bright smile, "
    "11 year old son with short black hair, casual t-shirt, laughing, "
    "steaming nikujaga on table, four sets of chopsticks, "
    "warm home dining room, evening meal, flash lighting, "
    "cinematic photography, 35mm film aesthetic",
    OUT_PRO,
    refine_steps=[
        ("makoto40", {"fw":0.45, "cfg":7.5, "doll":0.0, "dt":0.0, "denoise":0.5,
                      "prompt": "40 year old father, salt and pepper hair, silver glasses",
                      "neg": NEG_MALE}),
        ("yuriko34", {"fw":0.3, "cfg":10.0, "doll":0.0, "dt":0.2, "denoise":0.45,
                      "prompt": "34 year old mother, gentle face, tears of joy",
                      "neg": NEG_YURIKO}),
        ("shiori14", {"fw":0.8, "cfg":7.0, "doll":0.5, "dt":0.2, "denoise":0.45,
                      "prompt": "14 year old daughter, long black hair, bright smile",
                      "neg": NEG_CHILD}),
        ("tsubasa11",{"fw":0.8, "cfg":7.0, "doll":0.5, "dt":0.2, "denoise":0.45,
                      "prompt": "11 year old son, short black hair, laughing boy",
                      "neg": NEG_CHILD}),
    ],
    neg=NEG, cfg=7.5)

# P4: ソファの誠 — IPAdapter only
gen_makoto40("prologue04_sofa",
    "white shirt, no tie, casual pants, "
    "sitting on sofa in living room, leaning head back, eyes closed, "
    "relaxed tired expression, slight smile, "
    "warm living room at night, soft lamplight, "
    "peaceful atmosphere, japanese living room, quiet evening",
    OUT_PRO)


# ============================================================
# 第1章
# ============================================================
print("\n" + "="*50)
print("第1章")
print("="*50)

# C1: 通勤電車 — IPAdapter only
gen_makoto40("chapter1_01_train",
    "navy suit, white dress shirt, dark red tie, "
    "standing on train, holding overhead strap, "
    "looking at own reflection in window, "
    "morning commute, sobu line train, "
    "half-empty train car, april morning light, "
    "resignation envelope visible in breast pocket, "
    "contemplative expression, last commute, "
    "cityscape passing outside window",
    OUT_C1)

# C2: 部長デスク — FaceID (単体)
gen_faceid("chapter1_02_bucho",
    "bucho",
    f"{PB}, "
    "japanese department chief, 55 years old, thin face, silver glasses, "
    "short salt and pepper hair, slim build, "
    "navy suit, white shirt, striped tie, "
    "sitting at office desk, looking at resignation letter on table, "
    "white envelope with resignation written in kaisho, "
    "calm serious expression, marunouchi office, "
    "morning light through window, corporate atmosphere",
    OUT_C1,
    params={"fw":0.8, "cfg":8.0, "doll":0.0, "dt":0.2, "neg": NEG_MALE})

# C3: 葬儀 — txt2img → 誠IPAdapter → 叔母FaceID
gen_multichar("chapter1_03_funeral",
    f"{PB}, "
    "japanese funeral hall in sapporo, april, light snow outside window, "
    "late 20s japanese man in black funeral suit, silver glasses, "
    "holding a paper bag with small wooden box inside, quiet solemn expression, "
    "60 year old japanese woman, simple dark dress, kind tired face, "
    "handing the paper bag to the young man, "
    "small funeral venue, few relatives in background, "
    "snow flurries visible through window, "
    "emotional inheritance scene, cinematic photography",
    OUT_C1,
    refine_steps=[
        ("oba", {"fw":0.8, "cfg":8.0, "doll":0.0, "dt":0.2, "denoise":0.5,
                 "prompt": "60 year old japanese woman, simple dark dress, kind face, handing paper bag",
                 "neg": NEG}),
    ],
    neg=NEG, cfg=7.5)

# C4: 人形発見 — txt2img → 百合子FaceID
gen_multichar("chapter1_04_doll",
    f"{PB}, "
    "japanese living room, opening antique wooden box on table, "
    "34 year old woman with mid-length dark hair, gentle oval face, "
    "wearing casual home clothes, looking surprised and curious, "
    "antique french doll with porcelain face, blonde curly hair, "
    "blue glass eyes, floral print dress, sitting in open box, "
    "warm afternoon light through window, "
    "gold coins visible beside doll on table, "
    "intimate discovery scene, nostalgic atmosphere",
    OUT_C1,
    refine_steps=[
        ("yuriko34", {"fw":0.3, "cfg":10.0, "doll":0.0, "dt":0.2, "denoise":0.5,
                      "prompt": "34 year old woman, surprised curious expression, looking at doll",
                      "neg": NEG_YURIKO}),
    ],
    neg=NEG, cfg=7.5)

# C5: 栞と人形 (ファスナー) — FaceID txt2img (単体＋プロップ)
gen_faceid("chapter1_05_shiori",
    "shiori3",
    f"{PB_SHIORI3}, "
    "wearing pajamas, sleepy morning look, "
    "holding antique french doll in both hands, "
    "doll with porcelain face, blue glass eyes, floral dress, "
    "turning doll around to show back zipper, "
    "pointing at hidden zipper on doll's back with small finger, "
    "japanese living room, morning light, tatami floor, "
    "warm family home atmosphere, precious discovery moment",
    OUT_C1,
    params={"fw":0.5, "cfg":7.0, "doll":0.5, "dt":0.2, "neg": NEG_CHILD})


print("\n" + "="*50)
print("全完了")
print(f"  プロローグ: {OUT_PRO}")
print(f"  第1章:     {OUT_C1}")
print("="*50)
