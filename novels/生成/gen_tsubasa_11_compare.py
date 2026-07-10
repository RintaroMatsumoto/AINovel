"""翼11歳: 誠seed(1193774) vs 百合子seed(5977) 各5枚"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA, LS = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR = "tsubasa"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘翼\02_11歳_小学生"

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "feminine, woman, female features, effeminate, androgynous, "
       "makeup, long hair, colored hair")

SEEDS = [1193774, 5977]

SCENES = [
    ("front_smile", "front view, standing, smiling happily, looking at camera, school uniform, white shirt, navy shorts, backpack, sunny schoolyard"),
    ("threeq_play", "three-quarter view, playing at park, running, happy child, t-shirt and shorts, sneakers, afternoon sunlight"),
    ("home_casual", "sitting on living room floor, playing with toy, concentrated happy face, casual home clothes, warm lighting"),
    ("portrait", "front portrait, school uniform, white shirt, neat hair, innocent child smile, bright eyes, close-up"),
    ("street_walk", "walking on street, holding mother's hand implied, looking up, graphic t-shirt, denim shorts, sunset light"),
]

def gen_one(seed, tag, scene_desc, out_dir, prefix):
    prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
              f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
              f"11 year old japanese boy, elementary school student, "
              f"short black hair, small thin build, "
              f"{scene_desc}")
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0],"clip":["1",1],"lora_name":"DetailTweaker.safetensors","strength_model":0.2,"strength_clip":0.2}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip":["2",1]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["2",1]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "6": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["2",0],"positive":["4",0],"negative":["3",0],"latent_image":["5",0]}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples":["6",0],"vae":["1",2]}},
        "8": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix,"images":["7",0]}},
    }
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
                            params = urllib.parse.urlencode({"filename":img["filename"],"subfolder":img["subfolder"],"type":img["type"]})
                            url = f"{BASE}/view?{params}"
                            outpath = os.path.join(out_dir, img["filename"])
                            resp = requests.get(url, timeout=60)
                            if len(resp.content) > 1000:
                                with open(outpath,"wb") as f: f.write(resp.content)
                                print(f"  {prefix} OK ({len(resp.content)//1024}kb)")
                            else:
                                print(f"  {prefix} TOOSMALL")
                    return
                elif st == "error":
                    print(f"  {prefix} ERROR"); return
        except:
            if j == 299: print(f"  {prefix} TIMEOUT")

os.makedirs(OUT, exist_ok=True)

for seed in SEEDS:
    parent = "makoto" if seed == 1193774 else "yuriko"
    print(f"\n=== {parent} seed ({seed}) x 5 ===")
    for i, (tag, desc) in enumerate(SCENES, 1):
        seed_use = seed + i  # slightly vary seed for variety within same parent
        prefix = f"{CHAR}_11_{parent}s{seed}_{tag}"
        print(f"[{parent} {i}/5] {tag}")
        gen_one(seed_use, tag, desc, OUT, prefix)
        time.sleep(0.3)

print("\n完了。")
