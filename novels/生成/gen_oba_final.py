"""叔母: majicMIX 部長同パラメータ 5枚"""
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
       "mutated hands, mutated fingers, extra hands, extra arms, extra limbs, "
       "bad hands, bad fingers, missing fingers, missing hands, "
       "deformed hands, deformed fingers, multiple arms, multiple hands, "
       "watermark, signature, text, logo, "
       "young, girl, teen, 20s, 30s, 40s, "
       "heavy makeup, lipstick, eyeshadow, blush, "
       "kimono, japanese traditional clothing, yukata, "
       "decrepit, senile, dying, sick, "
       "extreme aged, ancient, hunched, crippled, "
       "horror, ghost, haunted, dark, spooky, scary")

SCENES = [
    "1woman, 65 year old japanese woman, aunt, gray streaked hair swept back, natural mature face, slight wrinkles around eyes, wearing formal black mourning dress, simple black blazer, calm dignified expression, portrait, neutral background, soft natural light",
    "1woman, 65 year old japanese lady, aunt, salt and pepper shoulder length hair, natural age lines, mature face, formal black dress, black jacket, plain background, tired but composed expression, head and shoulders portrait",
    "1woman, 65 year old japanese woman portrait, gray hair neat simple style, natural mature beauty, minimal wrinkles, wearing black mourning attire, simple black top, dignified expression, soft lighting, plain background",
    "1woman, 65 year old japanese aunt, gray hair pulled back, graceful aging, wearing formal black dress, black cardigan, gentle tired eyes, composed expression, three-quarter portrait, neutral background, natural light",
    "1woman, 65 year old japanese woman, salt and pepper hair in simple bun, natural aged skin, wearing black mourning outfit, simple blazer, quiet dignified look, half body portrait, soft window light",
]

for i, scene in enumerate(SCENES, 1):
    seed = random.randint(100000000, 999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
              f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
              f"{scene}")
    prefix = f"oba_majic_v4_cfg{CFG}_s{seed}_{i:02d}"

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
