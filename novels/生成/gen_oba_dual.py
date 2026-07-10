"""叔母: Dual IPAdapter (FaceID + 髪型) 百合子方式"""
import requests, json, time, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "majicMIX.safetensors"
W, H, STEPS, CFG = 512, 768, 30, 8.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\叔母\01_60代_札幌"
REF = OUT + r"\oba_faceid_cfg8.0_s443699833_03_00001_.png"
os.makedirs(OUT, exist_ok=True)

NEG = ("(worst quality:1.4), (low quality:1.4), EasyNegative, badhandv4, "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "mutated hands, extra hands, bad hands, deformed hands, "
       "v-neck, low neck, plunging, sleeveless, bare arms, bare shoulders, bare skin, "
       "open collar, deep neckline, cleavage, "
       "red, blue, green, white, brown, beige, gray, "
       "colored, colorful, patterned, striped, "
       "navy, dark blue, dark gray, charcoal, "
       "pink, purple, pastel, bright, light, "
       "fashionable, trendy, modern, elegant, chic, "
       "kimono, wafuku, japanese traditional, "
       "thin, skinny, slender, lean, slim, "
       "smiling, laughing, happy, cheerful")

SCENES = [
    "japanese elderly woman, 65, aunt, plump chubby fuller figure, gray white hair, natural makeup, wearing all black mourning dress, high neck, long sleeves, skirt below knees, single strand pearl necklace, portrait, neutral background, dignified tired expression",
    "japanese elderly woman, 65, aunt, plump body, gray white hair, light makeup, all black funeral outfit, closed neck, long sleeves, knee length skirt, pearl necklace, plain background, composed look",
    "japanese elderly woman, 65, aunt, chubby fuller build, gray white hair, natural makeup, black mourning attire, high collar, long sleeves, long skirt covering knees, pearl necklace, portrait, neutral bg",
    "japanese elderly woman, 65, aunt, plump figure, gray white hair, light daytime makeup, simple black funeral dress, high neckline, long sleeves, skirt below knee, pearl strand necklace, quiet tired eyes, portrait",
    "japanese elderly woman, 65, aunt, fuller figure chubby, gray white hair, natural makeup, all black mourning dress, closed neck, long sleeves, long skirt, pearl necklace, dignified portrait, neutral background",
]

print("Uploading ref (Dual IPAdapter)...")
with open(REF, "rb") as f:
    r = requests.post(f"{BASE}/upload/image", files={"image": ("oba_face.png", f, "image/png")}, timeout=30)
FACE_NAME = r.json()["name"]
print(f"  Face ref: {FACE_NAME}")

with open(REF, "rb") as f:
    r = requests.post(f"{BASE}/upload/image", files={"image": ("oba_hair.png", f, "image/png")}, timeout=30)
HAIR_NAME = r.json()["name"]
print(f"  Hair ref: {HAIR_NAME}")

for i, scene in enumerate(SCENES, 1):
    seed = random.randint(100000000, 999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, (Realistic, photorealistic:1.3), ultra detailed, "
              f"({scene})")
    prefix = f"oba_dual_fid_s{seed}_{i:02d}"

    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "CLIPSetLastLayer", "inputs": {"clip":["1",1], "stop_at_clip_layer":-2}},
        "3": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["1",0],"preset":"FACEID PLUS V2","lora_strength":0.5,"provider":"CPU"}},
        "4": {"class_type": "LoadImage", "inputs": {"image": FACE_NAME}},
        "5": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU","model_name":"buffalo_l"}},
        "6": {"class_type": "IPAdapterFaceID", "inputs": {"model":["3",0],"ipadapter":["3",1],"image":["4",0],"weight":0.8,"weight_faceidv2":0.0,"weight_type":"linear","combine_embeds":"concat","start_at":0.0,"end_at":1.0,"embeds_scaling":"V only","insightface":["5",0]}},
        "7": {"class_type": "IPAdapterUnifiedLoader", "inputs": {"model":["6",0],"preset":"STANDARD (medium strength)"}},
        "8": {"class_type": "LoadImage", "inputs": {"image": HAIR_NAME}},
        "9": {"class_type": "IPAdapter", "inputs": {"model":["7",0],"ipadapter":["7",1],"image":["8",0],"weight":0.25,"start_at":0.0,"end_at":1.0,"weight_type":"standard"}},
        "10": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip":["2",0]}},
        "11": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["2",0]}},
        "12": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "13": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["9",0],"positive":["11",0],"negative":["10",0],"latent_image":["12",0]}},
        "14": {"class_type": "VAEDecode", "inputs": {"samples":["13",0],"vae":["1",2]}},
        "15": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix,"images":["14",0]}},
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

print("\n完了 (Dual IPAdapter)")
