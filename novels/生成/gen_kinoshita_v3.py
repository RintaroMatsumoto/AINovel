"""木下v3: 会社員服装・普通OL 5枚"""
import requests, json, time, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "majicMIX.safetensors"
W, H, STEPS, CFG = 512, 768, 30, 8.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\木下\01_30代_経理課"
os.makedirs(OUT, exist_ok=True)

NEG = ("(worst quality:1.4), (low quality:1.4), EasyNegative, badhandv4, "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "mutated hands, extra hands, bad hands, deformed hands, extra fingers, "
       "handsome, beautiful, pretty, cute, attractive, gorgeous, "
       "model, fashion model, actor, actress, celebrity, "
       "charming, sexy, alluring, elegant, stylish, trendy, "
       "makeup, lipstick, blush, eyeshadow, mascara, eyeliner, "
       "young, youthful, fresh face, clear skin, radiant, "
       "slim, slender, fit, athletic, "
       "smiling, laughing, happy, cheerful, "
       "kimono, yukata, wafuku, casual wear, t-shirt, hoodie, "
       "sportswear, tracksuit, jeans, sneakers")

PROMPT_BASE = ("(masterpiece, best quality:1.2), 8k, (Realistic, photorealistic:1.3), ultra detailed, "
               "japanese woman, mid 30s, office lady, plain average face, not pretty, "
               "dark circles under eyes, tired, plain simple hair, no makeup, "
               "wearing office clothes, navy blazer, white blouse, formal work skirt, proper business attire")

SCENES = [
    "sitting at office desk with piles of documents, typing, tired expression, navy blazer, office background, fluorescent light",
    "standing in office near filing cabinet, holding thick file folder, plain face tired, office lady suit, formal work clothes",
    "portrait, 35 year old japanese office lady, plain unattractive face, tired eyes, navy blazer, white blouse, proper office wear",
    "sitting at cubicle desk, looking at papers with tired eyes, surrounded by document stacks, office lady in blazer and blouse",
    "standing in office hallway, carrying documents, walking slowly, plain tired face, navy blazer, white blouse, formal office skirt",
]

for i, scene in enumerate(SCENES, 1):
    seed = random.randint(100000000, 999999999)
    prompt = f"{PROMPT_BASE}, {scene}"
    prefix = f"kinoshita_v3_cfg{CFG}_s{seed}_{i:02d}"

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
