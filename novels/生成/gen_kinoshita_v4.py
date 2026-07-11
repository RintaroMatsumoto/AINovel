"""木下v4: モブキャラOL 5枚（既存ファイル維持）"""
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
       "young, youthful, fresh, clear skin, "
       "slim, slender, fit, toned, "
       "distinctive, memorable, outstanding, remarkable, special, "
       "smiling, laughing, happy, cheerful, "
       "t-shirt, hoodie, jeans, casual, sneakers, sportswear")

PROMPT = ("(masterpiece, best quality:1.2), 8k, (Realistic, photorealistic:1.3), ultra detailed, "
          "forgettable background character, nobody, "
          "japanese woman office worker, mid 30s, boring average face, "
          "unremarkable features, nothing special, plain dull eyes, "
          "simple boring hairstyle, no makeup, "
          "wearing standard navy office blazer, white blouse, plain work skirt")

for i in range(5):
    seed = random.randint(100000000, 999999999)
    scene = [
        "sitting at messy desk with document piles, tired blank expression, fluorescent office light, boring work clothes",
        "standing near office copier, holding papers, dull blank expression, standard office wear, plain background",
        "portrait, boring office lady, forgettable face, unremarkable features, simple blazer and blouse, office lighting",
        "sitting in cubicle surrounded by papers, tired forgettable expression, standard navy work clothes, nobody special",
        "walking in office corridor with documents, plain unremarkable face, boring work clothes, background character"
    ][i]
    prompt = f"{PROMPT}, {scene}"
    prefix = f"kinoshita_v4_cfg{CFG}_s{seed}_{i+1:02d}"

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
        print(f"  [{i+1}/5] SUBMIT: {e}"); continue

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
                                print(f"  [{i+1}/5] OK ({len(resp.content)//1024}kb)")
                            else:
                                print(f"  [{i+1}/5] TOOSMALL")
                    break
                elif st == "error":
                    print(f"  [{i+1}/5] ERROR"); break
        except:
            if j == 299: print(f"  [{i+1}/5] TIMEOUT")
    time.sleep(0.3)

print("\n完了")
