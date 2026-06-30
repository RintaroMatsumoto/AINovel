"""
橘百合子 18歳 再生成: 私服×5, 会社×5 (バラけseed, もっと地味に)
Usage: py novels/生成/gen_yuriko_v3.py
"""

import requests, json, time, urllib.request, os

BASE = "http://100.112.59.35:18188"
CHECKPOINT = "yayoi_mix.safetensors"
LORA1 = "JapaneseDollLikeness_v15.safetensors"
LORA1_S = 0.5
LORA2 = "DetailTweaker.safetensors"
LORA2_S = 0.2
WIDTH, HEIGHT = 512, 768
STEPS, CFG = 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"

OUT_DIR = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\02_18歳_回想_新入社員"
os.makedirs(OUT_DIR, exist_ok=True)

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "makeup, frills, lace, ribbon, glitter, high heels, long nails, pearl necklace, earrings")

VARIANTS = {
    "yuriko_casual_v3": (
        "私服",
        # 金のない高卒新入社員の私服：古い安物セーター、くたびれたスカート、使い古したスニーカー
        "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
        "18 year old japanese young woman, long straight black hair reaching mid-back, simple natural loose hair, "
        "earnest innocent face, no makeup, tired honest eyes, slender, very fair skin, "
        "old cheap sweater, worn plain skirt, old scuffed sneakers, "
        "urban street, cloudy day, shy poor girl, no money for fashion, "
        "looking down slightly, frugal modest vibe, not pretty just plain, t_yuriko_f"
    ),
    "yuriko_office_v3": (
        "会社",
        # 最安の事務員スーツ：型崩れジャケット、無地ブラウス、ひざ丈ストレートスカート、安パンプス
        # 髪はゴムで一つ結び（無造作、整えていない）
        "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
        "18 year old japanese young woman, long straight black hair tied in simple messy ponytail, "
        "earnest innocent face, no makeup, tired honest eyes, slender, very fair skin, "
        "cheap ill-fitting navy office jacket, plain no-frill white button-up blouse, "
        "knee length straight skirt, worn low heel pumps, "
        "office hallway, fluorescent light, diligent poor new employee, "
        "no accessories, frugal plain look, t_yuriko_f"
    ),
}

def gen_one(variant_name, label, prompt, seed):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model": ["1",0], "clip":["1",1], "lora_name":LORA1, "strength_model":LORA1_S, "strength_clip":LORA1_S}},
        "9": {"class_type": "LoraLoader", "inputs": {"model": ["2",0], "clip":["2",1], "lora_name":LORA2, "strength_model":LORA2_S, "strength_clip":LORA2_S}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["9",1]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["9",1]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width":WIDTH, "height":HEIGHT, "batch_size":1}},
        "6": {"class_type": "KSampler", "inputs": {"seed":seed, "steps":STEPS, "cfg":CFG, "sampler_name":SAMPLER, "scheduler":SCHEDULER, "denoise":1.0, "model":["9",0], "positive":["3",0], "negative":["4",0], "latent_image":["5",0]}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples":["6",0], "vae":["1",2]}},
        "8": {"class_type": "SaveImage", "inputs": {"filename_prefix":variant_name, "images":["7",0]}},
    }
    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status()
        pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  SUBMIT ERROR: {e}")
        return False
    for j in range(120):
        time.sleep(2)
        try:
            h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
            if pid in h:
                st = h[pid]["status"]["status_str"]
                if st == "success":
                    for nid, node in h[pid]["outputs"].items():
                        for img in node.get("images",[]):
                            url = f"{BASE}/view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
                            out = os.path.join(OUT_DIR, img["filename"])
                            urllib.request.urlretrieve(url, out)
                            print(f"  [{label} s{seed}] OK {img['filename']} ({os.path.getsize(out)//1024}kb)")
                    return True
                elif st == "error":
                    print(f"  [{label} s{seed}] JOB ERROR")
                    return False
        except:
            if j == 119:
                print(f"  [{label} s{seed}] TIMEOUT")
                return False
    return False

if __name__ == "__main__":
    # バラけseed: 非連続で広く散布
    casual_seeds = [3251, 3277, 3303, 3329, 3355]
    office_seeds = [3381, 3407, 3433, 3459, 3485]

    print("=== 私服 v3 (seeds: %s) ===" % casual_seeds)
    for s in casual_seeds:
        gen_one("yuriko_casual_v3", "私服v3", VARIANTS["yuriko_casual_v3"][1], s)
        time.sleep(0.3)

    print("\n=== 会社 v3 (seeds: %s) ===" % office_seeds)
    for s in office_seeds:
        gen_one("yuriko_office_v3", "会社v3", VARIANTS["yuriko_office_v3"][1], s)
        time.sleep(0.3)
