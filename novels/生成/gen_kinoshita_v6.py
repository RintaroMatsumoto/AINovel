"""木下v6: iNiverseMixモデルでモブ生成"""
import requests, json, time, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "iNiverseMix_real.safetensors"
W, H, STEPS, CFG = 512, 768, 30, 8.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\木下\01_30代_経理課"
os.makedirs(OUT, exist_ok=True)

NEG = ("worst quality, low quality, EasyNegative, badhandv4, "
       "cartoon, anime, illustration, painting, 3d render, "
       "beautiful, pretty, cute, attractive, model, "
       "makeup, lipstick, blush, "
       "young, youthful, fresh, radiant, "
       "smiling, laughing, happy, "
       "t-shirt, hoodie, jeans, casual")

SCENES = [
    "35 year old japanese woman, office worker, tired plain face, double chin, overweight, puffy eyes, wrinkles, cheap navy blazer too tight, white blouse, office desk with papers, boring expression",
    "35 year old japanese female, office lady, chubby, tired puffy face, dark eye bags, plain boring hair, cheap ill-fitting office jacket, white shirt, plain work skirt, holding folder, tired blank look",
    "35 year old japanese office woman, fat round face, double chin, tired droopy eyes, plain messy hair, cheap tight navy blazer, white blouse buttoned tight, neutral deadpan expression, desk background",
    "35 year old japanese woman, office worker, overweight, tired swollen face, big eye bags, uneven skin, plain boring hair, wrinkled navy suit jacket, white shirt, office corridor, blank tired expression",
    "35 year old japanese female office lady, chubby round face, tired puffy eyes, eye bags, sallow skin, messy plain hair, cheap office blazer straining at buttons, white blouse, cubicle with papers, dead tired expression"
]

for i, scene in enumerate(SCENES, 1):
    seed = random.randint(100000000, 999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, (Realistic, photorealistic:1.3), ultra detailed, "
              f"{scene}")
    prefix = f"kinoshita_v6_cfg{CFG}_s{seed}_{i:02d}"

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

print("\n完了")
