"""
橘百合子 18歳 seed3013系: 私服×5, 会社×5
Usage: py novels/生成/gen_yuriko_3013.py
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
       "makeup, heavy makeup, lipstick, mascara, eyeliner, blush, "
       "frills, lace, ribbon, glitter, high heels, long nails, "
       "earrings, necklace, accessories, perm, wavy, curly")

PROMPTS = {
    # 当時の一般的なOL制服：
    # ノーカラージャケット（ベージュ/グレー）、フリルなしブラウス、フレアスカートorタイトスカートひざ丈、パンプス
    # 百合子は高卒で貧乏なので安物だが、「一般的なOL」の範疇を出ない
    "yuriko_office_3013": (
        "会社",
        "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
        "18 year old japanese young woman, petite small frame, short stature, "
        "medium short black straight hair at chin length, neat simple hairstyle, "
        "naive unsophisticated girl, no makeup, shy nervous expression, "
        "2008 typical japanese office lady uniform, "
        "no-collar beige office jacket, plain white button-up blouse, "
        "knee length straight skirt, black low heel pumps, "
        "office hallway, modest new employee, day shift start, t_yuriko_f"
    ),
    # 私服：地味な色合い（グレー/ベージュ/紺/黒）、肌露出最小
    # 長袖・ハイネック・ロングスカート
    "yuriko_casual_3013": (
        "私服",
        "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
        "18 year old japanese young woman, petite small frame, short stature, "
        "medium short black straight hair at chin length, simple natural hairstyle, "
        "naive unsophisticated girl, no makeup, shy downcast eyes, "
        "dull plain casual clothes, "
        "long sleeve gray cardigan, high neck white shirt, "
        "ankle length dark skirt, old flat sneakers, "
        "urban street, cloudy weather, modest conservative dresser, "
        "no skin exposure, t_yuriko_f"
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
    # seed 3013 を基準にバラけさせた5 seeds
    office_seeds = [3801, 3827, 3853, 3879, 3905]
    casual_seeds = [3931, 3957, 3983, 4009, 4035]

    for variant_name, (label, prompt) in PROMPTS.items():
        seeds = office_seeds if "office" in variant_name else casual_seeds
        print(f"\n=== {label} (seeds: {seeds}) ===")
        for s in seeds:
            gen_one(variant_name, label, prompt, s)
            time.sleep(0.3)
