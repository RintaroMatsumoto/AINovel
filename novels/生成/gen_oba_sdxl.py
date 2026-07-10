"""叔母: RealVisXL Lightning 5枚"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "RealVisXL_V5.0_fp16.safetensors"
W, H = 1024, 1024
STEPS, CFG = 5, 1.5
SAMPLER, SCHEDULER = "dpmpp_sde_gpu", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\叔母\01_60代_札幌"
os.makedirs(OUT, exist_ok=True)

NEG = "worst quality, low quality, illustration, 3d, 2d, painting, cartoon, sketch, open mouth, deformed, extra limbs, bad anatomy, watermark, text"

SCENES = [
    "1 elderly japanese woman, 65 years old, aunt, gray streaked hair in bun, natural aged face with wrinkles, wearing formal black mourning clothes, black kimono, standing in traditional japanese room with buddhist altar, holding a small wrapped box in both hands, tired sad eyes, composed expression, afternoon light, hokkaido traditional house",
    "1 elderly japanese woman, 65 years old, aunt, gray hair pulled back neatly, mature wrinkled face, wearing full black mourning kimono, obi belt, sitting on tatami floor in traditional room, sliding door background, hands resting on lap, quiet dignified grief, soft daylight",
    "1 japanese elderly woman portrait, 60s, gray streaked hair, natural aging skin, wearing formal black mourning dress, simple pearl necklace, tired gentle eyes, slight sad smile, traditional japanese interior background, soft natural light, funeral gathering",
    "1 elderly japanese woman, 65 years old, aunt, salt and pepper gray hair, reading glasses, wearing black formal mourning clothes, standing by closet (oshiire) in traditional japanese room, reaching for an old box on shelf, traditional wooden interior, tatami floor, afternoon light",
    "1 elderly japanese woman, 60s, aunt, gray hair in simple style, wrinkled kind face, wearing formal black mourning dress, standing in traditional japanese living room with buddhist altar visible, holding an old package wrapped in cloth, looking down at it gently, warm soft light",
]

# VAE is baked in RealVisXL Lightning

for i, scene in enumerate(SCENES, 1):
    seed = random.randint(100000000, 999999999)
    prompt = f"(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, {scene}"
    prefix = f"oba_sdxl_Lightning_cfg{CFG}_s{seed}_{i:02d}"

    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip":["1",1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["1",1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "5": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["1",0],"positive":["3",0],"negative":["2",0],"latent_image":["4",0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples":["5",0],"vae":["1",2]}},
        "7": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix,"images":["6",0]}},
    }

    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status()
        pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  [{i}/5] SUBMIT: {e}"); continue

    for j in range(300):
        time.sleep(1)
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
                                print(f"  [{i}/5] OK ({len(resp.content)//1024}kb)")
                            else:
                                print(f"  [{i}/5] TOOSMALL")
                    break
                elif st == "error":
                    print(f"  [{i}/5] ERROR"); break
        except:
            if j == 299: print(f"  [{i}/5] TIMEOUT")
    time.sleep(0.2)

print("\n完了。5枚生成 (RealVisXL Lightning 1024x1024)")
