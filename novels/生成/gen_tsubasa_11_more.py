"""翼11歳: 誠seed vs 百合子seed さらに10枚ずつ バラエティ拡大"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
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

def gen_one(seed, prompt, prefix):
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
                            outpath = os.path.join(OUT, img["filename"])
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

BASE_PROMPT = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
               "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
               "11 year old japanese boy, elementary school student, "
               "short black hair, small thin build, cute boy face, ")

SCENES = [
    "school uniform, white button shirt, navy shorts, standing in classroom, front view, smiling",
    "casual clothes, graphic t-shirt, jeans, playing at park jungle gym, climbing, happy",
    "home clothes, pajamas, sitting on bed, reading comic book, concentrated, morning light",
    "school uniform, walking on path, trees, nature background, three-quarter view, looking ahead",
    "casual, hoodie, playing video game on sofa, excited expression, living room",
    "school uniform, at library, sitting at table, reading picture book, focused",
    "casual, striped t-shirt, shorts, riding bicycle, summer, wind in hair, laughing",
    "school uniform, standing at school entrance, backpack, waving, smiling at camera",
    "casual, sweater, sitting at desk, drawing with crayons, concentrated tongue out",
    "portrait, white shirt, close-up, looking up with big eyes, curious innocent expression",
]

for seed_base in [1193774, 5977]:
    parent = "makoto" if seed_base == 1193774 else "yuriko"
    print(f"\n=== {parent} seed x 10 ===")
    for i, scene in enumerate(SCENES, 1):
        seed = seed_base + i * 3 + 100
        prompt = BASE_PROMPT + scene
        prefix = f"{CHAR}_11_{parent}s{seed_base}_{i:02d}"
        print(f"[{parent} {i}/10]")
        gen_one(seed, prompt, prefix)
        time.sleep(0.3)

print("\n完了。")
