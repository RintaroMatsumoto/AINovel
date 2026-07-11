"""木下v7: majicMIX戻し・モブ顔＋会社員服装"""
import requests, json, time, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "majicMIX.safetensors"
W, H, STEPS, CFG = 512, 768, 30, 8.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\木下\01_30代_経理課"
os.makedirs(OUT, exist_ok=True)

NEG = ("(worst quality:1.4), (low quality:1.4), EasyNegative, badhandv4, "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "mutated hands, extra hands, bad hands, "
       "beautiful, pretty, cute, attractive, gorgeous, "
       "handsome, model, actress, celebrity, "
       "elegant, stylish, trendy, fashionable, chic, "
       "makeup, lipstick, blush, eyeshadow, mascara, "
       "young, youthful, fresh, radiant, glowing, "
       "slim, slender, fit, toned, thin, "
       "distinctive, memorable, outstanding, remarkable, "
       "smiling, laughing, happy, cheerful, bright, "
       "t-shirt, hoodie, jeans, casual, sneakers, "
       "japanese traditional, kimono")

SCENES = [
    "japanese woman office worker, mid 30s, chubby round face, double chin, tired puffy eyes, dirty blondish hair, dull yellow skin, boring average face, wearing navy office suit, white blouse, formal work skirt, sitting at messy desk with many papers, tired dull expression, office fluorescent light",
    "japanese office lady, 35, fat body, round chubby face, tired droopy eyes, eye bags, sallow complexion, plain medium hair, no style, wearing navy blazer too tight, white blouse, plain formal skirt, standing by filing cabinet, holding document, blank expression",
    "japanese woman, 35, working in office, overweight, double chin, tired puffy face, dark circles under eyes, blotchy skin, ordinary boring hairstyle, generic office wear, navy jacket, white shirt, work skirt, portrait in office cubicle, papers around, blank tired look",
    "japanese female office worker, mid 30s, chubby overweight, round face, dull tired eyes, puffy eye bags, uneven skin, ordinary hair in loose bun, wearing tight navy office blazer, white blouse, proper work skirt, desk full of documents, tired expression, office",
    "japanese office lady, 35 years old, fat build, round face double chin, tired bloodshot eyes, dark under-eye rings, pale dull skin, simple boring medium hair, cheap navy suit jacket, white blouse, formal black skirt, walking in hall with papers, tired blank look"
]

for i, scene in enumerate(SCENES, 1):
    seed = random.randint(100000000, 999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, (Realistic, photorealistic:1.3), ultra detailed, "
              f"{scene}")
    prefix = f"kinoshita_v7_cfg{CFG}_s{seed}_{i:02d}"

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

print("\n完了")
