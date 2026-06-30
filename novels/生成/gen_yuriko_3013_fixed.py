"""
橘百合子 18歳 seed3013固定 5カットずつ
Usage: py novels/生成/gen_yuriko_3013_fixed.py
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
SEED = 3013

OUT_DIR = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\02_18歳_回想_新入社員"
os.makedirs(OUT_DIR, exist_ok=True)

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "makeup, heavy makeup, lipstick, mascara, eyeliner, blush, "
       "frills, lace, ribbon, glitter, high heels, long nails, "
       "earrings, necklace, accessories, perm, wavy, curly, "
       "long hair, hair past ears")

# Base prompt (face/body constant) + angle/scene variation
BASE_CASUAL = (
    "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
    "18 year old japanese young woman, petite small frame, "
    "short black bob haircut, hair exactly at jawline, neck visible, "
    "plain natural face, no makeup, ordinary japanese girl, honest eyes, "
    "dull plain casual clothes, long sleeve gray cardigan, high neck white shirt, "
    "ankle length dark skirt, old flat sneakers, "
    "urban street cloudy day, modest conservative dresser, no skin exposure, t_yuriko_f"
)

BASE_OFFICE = (
    "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
    "18 year old japanese young woman, petite small frame, "
    "short black bob haircut, hair ends at jawline, neck visible, "
    "plain natural face, no makeup, ordinary japanese girl, honest eyes, "
    "standard company-issued office uniform 2008, "
    "navy no-collar office jacket with gold tone buttons, "
    "plain white blouse, knee length straight skirt, "
    "standard low heel pumps, slightly boxy fit, "
    "modest new employee, t_yuriko_f"
)

# Angle/scene variations appended to base
CASUAL_VARIANTS = [
    "standing on street sidewalk, looking straight at camera, both hands in pockets",
    "walking down street, three-quarter profile, looking slightly away, carrying plastic bag",
    "sitting on public bench, hands folded on lap, looking down with shy smile",
    "standing at street corner waiting for traffic light, side view, glancing to side",
    "standing in front of small park, looking up at sky, natural relaxed posture",
]

OFFICE_VARIANTS = [
    "standing in office corridor, looking straight at camera, holding notepad to chest",
    "standing by office desk, side profile, organizing papers, morning light through window",
    "walking through office hallway, three-quarter back view, glancing back over shoulder",
    "standing in front of office entrance, looking down adjusting jacket, nervous",
    "standing near water cooler, holding paper cup, slight awkward smile, new employee",
]


def gen_one(variant_name, base_prompt, angle_text, seed):
    prompt = base_prompt + angle_text
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
                            print(f"  [{variant_name}] OK {img['filename']} ({os.path.getsize(out)//1024}kb)")
                    return True
                elif st == "error":
                    print(f"  [{variant_name}] JOB ERROR")
                    return False
        except:
            if j == 119:
                print(f"  [{variant_name}] TIMEOUT")
                return False
    return False

if __name__ == "__main__":
    print(f"\n=== 私服（seed {SEED} 固定 × 5カット） ===")
    for i, angle in enumerate(CASUAL_VARIANTS):
        gen_one(f"yuriko_casual_3013_cut{i+1}", BASE_CASUAL, ", " + angle, SEED)
        time.sleep(0.3)

    print(f"\n=== 会社（seed {SEED} 固定 × 5カット） ===")
    for i, angle in enumerate(OFFICE_VARIANTS):
        gen_one(f"yuriko_office_3013_cut{i+1}", BASE_OFFICE, ", " + angle, SEED)
        time.sleep(0.3)
