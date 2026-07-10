"""叔母FaceID v2: 肌露出禁止・洋装喪服"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "majicMIX.safetensors"
W, H, STEPS, CFG = 512, 768, 30, 8.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\叔母\01_60代_札幌"
REF = OUT + r"\oba_majic_v4_cfg8.0_s876174573_03_00001_.png"
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
       "kimono, yukata, traditional japanese clothing, "
       "decrepit, senile, dying, sick, "
       "extreme aged, ancient, hunched, crippled, "
       "horror, ghost, haunted, dark, spooky, "
       "open collar, v-neck, low neck, bare neck, bare arms, bare shoulders, "
       "skin exposure, exposed skin, cleavage, décolletage, "
       "short sleeves, sleeveless, no sleeves")

SCENES = [
    "1woman, 65 year old japanese woman, aunt, gray streaked hair swept back, natural mature face, slight wrinkles, wearing formal black mourning dress, high neck, long sleeves, covered arms, closed collar, fully covered, portrait, neutral background, soft natural light",
    "1woman, 65 year old japanese lady, aunt, salt and pepper hair, mature face, formal black dress, high neckline, long sleeves, fully covered, no skin showing, plain background, composed expression",
    "1woman, 65 year old japanese woman portrait, gray hair neat style, wearing black mourning attire, high collar, long sleeves, covered neck and arms, dignified expression, soft lighting",
    "1woman, 65 year old japanese aunt, gray hair pulled back, wearing formal black dress, high neck, long sleeves, covered fully, gentle tired eyes, composed expression, half body portrait",
    "1woman, 65 year old japanese woman, salt and pepper hair, wearing black mourning outfit, high collar, long sleeves, no exposed skin, quiet dignified look, front portrait, soft window light",
]

print("Uploading ref...")
with open(REF, "rb") as f:
    r = requests.post(f"{BASE}/upload/image", files={"image": ("oba_ref.png", f, "image/png")}, timeout=30)
REF_NAME = r.json()["name"]
print(f"  OK")

for i, scene in enumerate(SCENES, 1):
    seed = random.randint(100000000, 999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
              f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
              f"{scene}")
    prefix = f"oba_faceid_v2_cfg{CFG}_s{seed}_{i:02d}"

    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "CLIPSetLastLayer", "inputs": {"clip":["1",1], "stop_at_clip_layer":-2}},
        "3": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["1",0],"preset":"FACEID PLUS V2","lora_strength":0.5,"provider":"CPU"}},
        "4": {"class_type": "LoadImage", "inputs": {"image": REF_NAME}},
        "5": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU","model_name":"buffalo_l"}},
        "6": {"class_type": "IPAdapterFaceID", "inputs": {"model":["3",0],"ipadapter":["3",1],"image":["4",0],"weight":0.8,"weight_faceidv2":0.0,"weight_type":"linear","combine_embeds":"concat","start_at":0.0,"end_at":1.0,"embeds_scaling":"V only","insightface":["5",0]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip":["2",0]}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["2",0]}},
        "9": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "10": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["6",0],"positive":["8",0],"negative":["7",0],"latent_image":["9",0]}},
        "11": {"class_type": "VAEDecode", "inputs": {"samples":["10",0],"vae":["1",2]}},
        "12": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix,"images":["11",0]}},
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
