"""
橘栞13歳: seed 1193774 (誠参照顔) × 私服10枚
比較用: 百合子seed (5977) vs 誠seed (1193774)
M1 ComfyUI (100.112.59.35:18188) 使用
"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "JapaneseDollLikeness_v15.safetensors", 0.5
LORA2, L2S = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
SEED = 1193774  # 誠参照顔のseed
CHAR, AGE, MODEL = "shiori", "13", "yayoi_mix"

OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘栞\03_13歳_中学生_私服_誠seed"
os.makedirs(OUT, exist_ok=True)

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
print(f"橘栞13歳 seed比較: 誠seed {SEED}")
print(f"出力先: {OUT}")
print()

for i, (name, hair, clothes, pose) in enumerate(CASUAL_VARIANTS, 1):
    prompt = f"{BASE_FACE} {hair}, {clothes}, {pose}"
    prefix = f"{CHAR}_{AGE}_{MODEL}_s{SEED}_{name}"
    print(f"[{i}/10] {name}")
    gen_one(build_workflow(SEED, prompt, NEG, prefix), prefix, OUT)
    time.sleep(0.5)

print()
print("完了。百合子seed (5977) と誠seed (1193774) を比較してください。")
