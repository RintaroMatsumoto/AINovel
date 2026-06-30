"""
橘百合子 18歳 追加生成: 私服×10, 会社×10
Usage: py novels/生成/gen_yuriko_2008.py
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
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character")

VARIANTS = {
    "yuriko_casual": (
        "私服",
        "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
        "18 year old japanese young woman, long straight black hair reaching mid-back, natural loose hairstyle down, "
        "earnest innocent face, honest modest eyes, no makeup, slender fair skin, "
        "plain cheap casual clothes, simple sweater and skirt, old worn sneakers, "
        "standing on street, daytime, shy expression, modest frugal girl, no dating experience, t_yuriko_f"
    ),
    "yuriko_office": (
        "会社",
        "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
        "18 year old japanese young woman, long straight black hair reaching mid-back, tied in low ponytail, neat office style, "
        "earnest innocent face, honest modest eyes, no makeup, slender fair skin, "
        "plain modest blouse, standard office jacket, knee length skirt, low heel pumps, "
        "office hallway, diligent hardworking new employee, serious studious vibe, t_yuriko_f"
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
    for variant_name, (label, prompt) in VARIANTS.items():
        base = 3211 if variant_name == "yuriko_casual" else 3221
        print(f"\n=== {label} (seeds {base}-{base+9}) ===")
        for i in range(10):
            seed = base + i
            gen_one(variant_name, label, prompt, seed)
            time.sleep(0.3)
