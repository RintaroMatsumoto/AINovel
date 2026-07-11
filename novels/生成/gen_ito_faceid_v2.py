"""伊藤FaceID v2: 男性固定強化"""
import requests, json, time, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "majicMIX.safetensors"
W, H, STEPS, CFG = 512, 768, 30, 8.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\伊藤\01_35歳_経理課"
REF = OUT + r"\採用\ito_v2_cfg8.0_s817771457_01_00001_.png"
os.makedirs(OUT, exist_ok=True)

NEG = ("(worst quality:1.4), (low quality:1.4), EasyNegative, badhandv4, "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "mutated hands, extra hands, bad hands, "
       "woman, female, feminine, feminine face, "
       "breasts, curves, makeup, lipstick, blush, "
       "beautiful, pretty, cute, attractive, "
       "handsome, model, actor, celebrity, "
       "elegant, stylish, trendy, fashionable, "
       "young, youthful, fresh, "
       "smiling, laughing, happy, "
       "long hair, colored hair, curly hair, "
       "t-shirt, hoodie, casual, "
       "distinctive, memorable, outstanding")

SCENES = [
    "sitting at office desk, front view, tired salaryman, navy suit, white shirt, tie, office background, overweight",
    "standing in office near water cooler, holding cup, pot belly visible, tired, navy suit, office",
    "portrait, 35 year old japanese man, fat face, double chin, tired eyes, navy suit, tie, office",
    "walking in office hallway, carrying documents, overweight tired salaryman, navy suit",
    "sitting at meeting table, boring expression, fat tired man, navy suit, office meeting",
    "at desk talking on phone, hand on forehead, tired stressed, navy suit, tie loosened",
    "in break room, drinking coffee, staring blankly, fat tired salaryman, white shirt, tie",
    "at desk typing, tired heavy expression, overweight, navy suit, white shirt, office",
    "standing by office window, looking out, tired back view, fat build, navy suit",
    "portrait half body, tired salaryman, double chin, receding hairline, navy suit and tie, office",
]

print("Upload ref...")
with open(REF, "rb") as f:
    r = requests.post(f"{BASE}/upload/image", files={"image": ("ito_ref.png", f, "image/png")}, timeout=30)
REF_NAME = r.json()["name"]
print(f"OK: {REF_NAME}")

for i, scene in enumerate(SCENES, 1):
    seed = random.randint(100000000, 999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, (Realistic, photorealistic:1.3), ultra detailed, "
              f"(male:1.4), (man:1.3), 1boy, "
              f"japanese salaryman, 35 years old, fat overweight, double chin, tired eyes, "
              f"receding hairline, plain ugly face, "
              f"{scene}")
    prefix = f"ito_fid_v2_cfg{CFG}_s{seed}_{i:02d}"

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
        print(f"  [{i}/10] SUBMIT: {e}"); continue

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
                                print(f"  [{i}/10] OK ({len(resp.content)//1024}kb)")
                            else:
                                print(f"  [{i}/10] TOOSMALL")
                    break
                elif st == "error":
                    print(f"  [{i}/10] ERROR"); break
        except:
            if j == 299: print(f"  [{i}/10] TIMEOUT")
    time.sleep(0.3)

print("\n完了")
