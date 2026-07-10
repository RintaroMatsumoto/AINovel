"""叔母v2: 若すぎず老けすぎず 5枚 majicMIX"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "majicMIX.safetensors"
W, H, STEPS, CFG = 512, 768, 30, 8.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\叔母\01_60代_札幌"
os.makedirs(OUT, exist_ok=True)

NEG = ("(worst quality:1.4), (low quality:1.4), (normal quality:1.2), "
       "EasyNegative, badhandv4, "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, plastic skin, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, "
       "young, girl, teen, 20s, 30s, 40s, "
       "heavy makeup, lipstick, eyeshadow, blush, "
       "smiling, laughing, happy, cheerful, "
       "decrepit, senile, dying, sick, bedridden, "
       "severe wrinkles, extreme aged, ancient, frail")

SCENES = [
    "1woman, 60 year old japanese woman, aunt, salt and pepper hair in simple bun, natural aging gracefully, minimal wrinkles, warm kind eyes, wearing simple blouse and cardigan, standing in traditional japanese room, holding a wrapped box, calm dignified expression",
    "1woman, 60 year old japanese lady, aunt, gray-streaked hair tied back, gentle wrinkles around eyes, natural aged face, simple knit sweater, sitting at low table, pouring tea, traditional japanese home, warm daylight",
    "1woman, 60 year old japanese woman portrait, shoulder length gray hair, natural mature face, slight wrinkles, graceful aging, modest collared shirt, soft expression, traditional interior background, gentle lighting",
    "1woman, 60 year old japanese aunt, salt and pepper hair, reading glasses, wearing comfortable cardigan, standing at entrance of old house, holding paper package, gentle concerned expression, hokkaido home",
    "1woman, 60 year old japanese woman, gray hair neat style, natural mature beauty, simple dress, standing in kitchen, holding old photograph, thoughtful expression, warm afternoon light",
]

print("Generating aunt v2...")
for i, scene in enumerate(SCENES, 1):
    seed = random.randint(100000000, 999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
              f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
              f"{scene}")
    prefix = f"oba_v2_majic_cfg{CFG}_s{seed}_{i:02d}"

    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "CLIPSetLastLayer", "inputs": {"clip":["1",1], "stop_at_clip_layer":-2}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip":["2",0]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["2",0]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "6": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["1",0],"positive":["4",0],"negative":["3",0],"latent_image":["5",0]}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples":["6",0],"vae":["1",2]}},
        "8": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix,"images":["7",0]}},
    }

    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status()
        pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  [{i}/5] SUBMIT: {e}"); continue

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
                                print(f"  [{i}/5] OK ({len(resp.content)//1024}kb)")
                            else:
                                print(f"  [{i}/5] TOOSMALL")
                    break
                elif st == "error":
                    print(f"  [{i}/5] ERROR"); break
        except:
            if j == 299: print(f"  [{i}/5] TIMEOUT")
    time.sleep(0.3)

print("\n完了。")
