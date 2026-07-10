"""叔母v7: 選定画像FaceID + 露出なし喪服"""
import requests, json, time, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "majicMIX.safetensors"
W, H, STEPS, CFG = 512, 768, 30, 8.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\叔母\01_60代_札幌"
REF = OUT + r"\oba_faceid_cfg8.0_s443699833_03_00001_.png"

NEG = ("(worst quality:1.4), (low quality:1.4), EasyNegative, badhandv4, "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "mutated hands, extra hands, bad hands, deformed hands, "
       "makeup, lipstick, blush, fashionable, stylish, model, "
       "young, beautiful, pretty, cute, glamour, "
       "v-neck, low neck, sleeveless, bare arms, bare shoulders, "
       "open collar, deep neckline, cleavage, "
       "smiling, laughing, happy, cheerful, "
       "red, blue, green, white, brown, beige, gray, "
       "colored clothes, colorful, patterned, striped, "
       "dark blue, navy, dark gray, charcoal, "
       "light color, pastel, bright, pink, purple")

SCENES = [
    "japanese elderly woman portrait, 65 years old, gray white hair, no makeup natural face, wearing all black funeral dress with high neckline, long sleeves, fully covered, black all clothing, plain neutral background, soft natural light",
    "japanese old woman, gray hair, 65, no makeup natural aged face, simple black funeral dress, black blazer over, high closed neck, long sleeves covering arms, all black outfit, no skin visible, neutral background",
    "elderly japanese female, 65, gray white hair, natural plain face, wearing all black mourning outfit, dress with closed neck and long sleeves, black cardigan, everything black, proper funeral wear, neutral bg",
    "japanese elderly woman, gray hair pulled back, 65, natural face no makeup, black funeral dress high neckline, long black sleeves, black cover, all black clothes completely covered, portrait, neutral background",
    "old japanese woman portrait, 65, gray salt pepper hair, plain no makeup face, wearing all black mourning dress, closed neck, long sleeves covering to wrists, black outer, all black proper funeral attire",
]

print("Upload ref...")
with open(REF, "rb") as f:
    r = requests.post(f"{BASE}/upload/image", files={"image": ("oba_ref2.png", f, "image/png")}, timeout=30)
REF_NAME = r.json()["name"]
print("OK")

for i, scene in enumerate(SCENES, 1):
    seed = random.randint(100000000, 999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, (Realistic, photorealistic:1.3), ultra detailed, "
              f"{scene}")
    prefix = f"oba_v7_fid_s{seed}_{i:02d}"

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

print("完了")
