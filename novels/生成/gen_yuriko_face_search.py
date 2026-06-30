"""
橘百合子 顔探索: seed探索 最小プロンプト×10枚
"""
import requests, json, time, urllib.request, os, random

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
       "makeup, frills, lace, ribbon, long hair, hair past ears, curly hair, wavy hair")

PROMPT = (
    "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
    "18 year old japanese young woman, petite small frame, "
    "short black bob haircut, hair ends at jawline, "
    "plain natural face, no makeup, "
    "simple white t-shirt, "
    "looking at camera, t_yuriko_f"
)

def gen_one(seed):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0],"clip":["1",1],"lora_name":LORA1,"strength_model":LORA1_S,"strength_clip":LORA1_S}},
        "9": {"class_type": "LoraLoader", "inputs": {"model":["2",0],"clip":["2",1],"lora_name":LORA2,"strength_model":LORA2_S,"strength_clip":LORA2_S}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": PROMPT, "clip":["9",1]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip":["9",1]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width":WIDTH,"height":HEIGHT,"batch_size":1}},
        "6": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["9",0],"positive":["3",0],"negative":["4",0],"latent_image":["5",0]}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples":["6",0],"vae":["1",2]}},
        "8": {"class_type": "SaveImage", "inputs": {"filename_prefix":f"yuriko_face_s{seed}","images":["7",0]}},
    }
    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status()
        pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  s{seed} SUBMIT ERROR: {e}")
        return
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
                            print(f"  s{seed} OK ({os.path.getsize(out)//1024}kb)")
                    return
                elif st == "error":
                    print(f"  s{seed} ERROR")
                    return
        except:
            if j == 119:
                print(f"  s{seed} TIMEOUT")
                return

if __name__ == "__main__":
    seeds = random.sample(range(4000, 9999), 10)
    print(f"Seeds: {seeds}")
    for s in seeds:
        gen_one(s)
        time.sleep(0.3)
