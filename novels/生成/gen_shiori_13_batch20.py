"""
橘栞13歳: seed 5977 × 制服10枚 + 私服10枚 = 計20枚
命名規則: 百合子準拠 ({char}_{age}_{model}_s{seed}_{variant}_00001_.png)
M1 ComfyUI (100.112.59.35:18188) 使用
"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "JapaneseDollLikeness_v15.safetensors", 0.5
LORA2, L2S = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
SEED = 5977
CHAR, AGE, MODEL = "shiori", "13", "yayoi_mix"

OUT_UNIFORM = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘栞\01_13歳_中学生_制服"
OUT_CASUAL = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘栞\02_13歳_中学生_私服"
os.makedirs(OUT_UNIFORM, exist_ok=True)
os.makedirs(OUT_CASUAL, exist_ok=True)

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "adult, mature, old, aging, wrinkles, "
       "heavy makeup, dark eyeshadow, lipstick, "
       "dyed hair, colored hair, blonde hair, brown hair")

BASE_FACE = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
             "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
             "13 year old japanese girl, second year middle school student, "
             "round childish face, baby fat still visible, "
             "small thin build, still growing, "
             "long straight black hair, neat bangs, ")

UNIFORM_VARIANTS = [
    ("uniform_front",
     "long straight black hair, neat bangs covering forehead",
     "navy blazer with gold buttons, white blouse, gray pleated skirt, navy ribbon tie, knee-high black socks, brown loafers",
     "front view, standing, facing camera, shy expression, school entrance"),
    ("uniform_threeq",
     "long straight black hair, neat bangs",
     "navy blazer with gold buttons, white blouse, gray pleated skirt, navy ribbon tie, knee-high black socks",
     "three-quarter view, standing, holding school bag, looking slightly to the side, school gate"),
    ("uniform_profile",
     "long straight black hair, neat bangs",
     "navy blazer with gold buttons, white blouse, gray pleated skirt, navy ribbon tie",
     "side view, profile, walking down school corridor, natural light from window"),
    ("uniform_desk",
     "long straight black hair, neat bangs",
     "navy blazer, white blouse, gray pleated skirt",
     "front view, sitting at desk, writing in notebook, focused, classroom"),
    ("uniform_threeq_desk",
     "long straight black hair, neat bangs",
     "navy blazer, white blouse, gray pleated skirt, ribbon tie loosened slightly",
     "three-quarter view, sitting at desk, looking up from book, classroom afternoon"),
    ("uniform_standing_window",
     "long straight black hair, light catching",
     "navy blazer with gold buttons, white blouse, gray pleated skirt, navy ribbon tie",
     "front view, standing by window, hands clasped in front, natural light, soft expression"),
    ("uniform_hallway",
     "long straight black hair, neat bangs",
     "navy blazer, white blouse, gray pleated skirt, school bag on shoulder",
     "three-quarter view, walking in hallway, looking back over shoulder, afternoon"),
    ("uniform_entrance",
     "long straight black hair, neat bangs",
     "navy blazer, white blouse, gray pleated skirt, indoor shoes in hand",
     "front view, standing at shoe locker, changing shoes, morning"),
    ("uniform_library",
     "long straight black hair, neat bangs",
     "navy blazer, white blouse, gray pleated skirt",
     "side view, sitting in library, reading book, quiet atmosphere, warm light"),
    ("uniform_courtyard",
     "long straight black hair, neat bangs, slight wind",
     "navy blazer with gold buttons, white blouse, gray pleated skirt, navy ribbon tie",
     "three-quarter view, standing in school courtyard, slight smile, afternoon sun"),
]

CASUAL_VARIANTS = [
    ("casual_tshirt_front",
     "long straight black hair, loose, no bangs styling",
     "plain white t-shirt, light blue denim jacket over shoulders",
     "front view, standing, facing camera, casual weekend, park"),
    ("casual_sweater_front",
     "long straight black hair, soft bangs",
     "oversized cream knit sweater, comfortable",
     "front view, sitting on sofa, hands in lap, warm home interior"),
    ("casual_sweater_threeq",
     "long straight black hair, soft bangs",
     "oversized cream knit sweater",
     "three-quarter view, sitting, looking out window, thoughtful, home"),
    ("casual_hoodie_front",
     "long straight black hair, slightly messy",
     "gray zip-up hoodie, plain t-shirt underneath",
     "front view, standing, hands in pocket, casual, convenience store background"),
    ("casual_hoodie_threeq",
     "long straight black hair, slightly messy",
     "gray zip-up hoodie, plain t-shirt underneath",
     "three-quarter view, walking outside, looking down, sidewalk"),
    ("casual_cardigan_front",
     "long straight black hair, neat bangs",
     "beige cardigan buttoned up, plaid skirt",
     "front view, sitting at cafe table, juice in front, shy expression"),
    ("casual_cardigan_side",
     "long straight black hair, neat bangs",
     "beige cardigan buttoned up, plaid skirt",
     "side view, standing at bookshelf, browsing books, profile"),
    ("casual_summer_front",
     "long straight black hair, tied low ponytail",
     "sleeveless white blouse, denim shorts, summer",
     "front view, standing, slight smile, bright outdoor, summer"),
    ("casual_pajama_front",
     "long straight black hair, messy, just woke up",
     "simple cotton pajama top, light blue with small pattern",
     "front view, sitting on bed, rubbing eyes, sleepy, morning, bedroom"),
    ("casual_weekend_threeq",
     "long straight black hair, loose, hair tucked behind ear",
     "striped long sleeve t-shirt, denim skirt, canvas sneakers",
     "three-quarter view, standing at park bench, afternoon, relaxed"),
]

def build_workflow(seed, prompt, neg, prefix):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model": ["1",0], "clip":["1",1], "lora_name":LORA1, "strength_model":L1S, "strength_clip":L1S}},
        "3": {"class_type": "LoraLoader", "inputs": {"model": ["2",0], "clip":["2",1], "lora_name":LORA2, "strength_model":L2S, "strength_clip":L2S}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip":["3",1]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["3",1]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "7": {"class_type": "KSampler", "inputs": {
            "seed":seed,"steps":STEPS,"cfg":CFG,
            "sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,
            "model":["3",0], "positive":["5",0], "negative":["4",0], "latent_image":["6",0]
        }},
        "8": {"class_type": "VAEDecode", "inputs": {"samples":["7",0], "vae":["1",2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix, "images":["8",0]}},
    }

def gen_one(wf, prefix, out_dir):
    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status()
        pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  {prefix} SUBMIT: {e}"); return
    for j in range(300):
        time.sleep(2)
        try:
            h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
            if pid in h:
                st = h[pid]["status"]["status_str"]
                if st == "success":
                    for nid, node in h[pid]["outputs"].items():
                        for img in node.get("images",[]):
                            params = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img["subfolder"], "type": img["type"]})
                            url = f"{BASE}/view?{params}"
                            outpath = os.path.join(out_dir, img["filename"])
                            resp = requests.get(url, timeout=60)
                            if len(resp.content) > 1000:
                                with open(outpath, "wb") as f: f.write(resp.content)
                                print(f"  {prefix} OK ({len(resp.content)//1024}kb)")
                            else:
                                print(f"  {prefix} EMPTY ({len(resp.content)}b)")
                    return
                elif st == "error":
                    print(f"  {prefix} ERROR"); return
        except:
            if j == 299: print(f"  {prefix} TIMEOUT")

# === MAIN ===
print(f"橘栞13歳 生成開始: seed {SEED}")
print(f"制服: {OUT_UNIFORM}")
print(f"私服: {OUT_CASUAL}")
print()

# 制服10枚
print("=== 制服版 10枚 ===")
for i, (name, hair, clothes, pose) in enumerate(UNIFORM_VARIANTS, 1):
    prompt = f"{BASE_FACE} {hair}, {clothes}, {pose}"
    prefix = f"{CHAR}_{AGE}_{MODEL}_s{SEED}_{name}"
    print(f"[{i}/10] {name}")
    gen_one(build_workflow(SEED, prompt, NEG, prefix), prefix, OUT_UNIFORM)
    time.sleep(0.5)

# 私服10枚
print()
print("=== 私服版 10枚 ===")
for i, (name, hair, clothes, pose) in enumerate(CASUAL_VARIANTS, 1):
    prompt = f"{BASE_FACE} {hair}, {clothes}, {pose}"
    prefix = f"{CHAR}_{AGE}_{MODEL}_s{SEED}_{name}"
    print(f"[{i}/10] {name}")
    gen_one(build_workflow(SEED, prompt, NEG, prefix), prefix, OUT_CASUAL)
    time.sleep(0.5)

print()
print("完了。計20枚生成。")
