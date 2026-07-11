"""木下v5: 具体的なモブ描写で再挑戦"""
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
       "perfect skin, symmetrical face, defined jawline, clear eyes, "
       "youthful, fresh, glowing, vibrant, radiant, "
       "fashionable, well-dressed, neat, tidy, "
       "beautiful, pretty, cute, attractive, gorgeous, "
       "handsome, model, actress, celebrity, "
       "elegant, stylish, trendy, fashionable, chic, "
       "makeup, lipstick, blush, eyeshadow, mascara, "
       "slim, slender, fit, toned, "
       "smiling, laughing, happy, cheerful, bright, "
       "t-shirt, hoodie, jeans, casual, sneakers")

SCENES = [
    "35 year old japanese office woman, chubby face, double chin, puffy tired eyes, dark bags under eyes, dull uneven skin, age spots on skin, mousy brown hair pulled back messily, wearing slightly wrinkled navy office blazer that is too tight, cheap white polyester blouse, plain knee-length skirt, generic office desk with stacks of papers, fluorescent office lighting, blank tired expression",
    "35 year old japanese office lady, overweight round body, double chin, tired puffy face, dark eye circles, dull yellowish skin tone, simple boring hairstyle with frizzy ends, wearing outdated navy office suit jacket that does not fit well, cheap white blouse, generic office corridor, holding thick folder, blank nothing expression",
    "35 year old japanese female office worker, round chubby face, tired droopy eyes, heavy eye bags, uneven skin texture, visible pores, simple boring shoulder length hair, slightly greasy, wearing cheap navy office blazer, white blouse buttoned to top, plain work skirt, desk background with document piles, dull tired office expression",
    "35 year old japanese woman in office, puffy round face, double chin, tired bloodshot eyes, dark under-eye circles, sallow skin, boring plain hairstyle with split ends, wearing tight-fitting navy blazer that pulls at buttons, plain white shirt, office cubicle surrounded by paper files, exhausted blank stare",
    "35 year old japanese office lady, overweight plump body, round puffy face, tired dull eyes with dark circles, uneven blotchy skin, simple boring hair in a loose bun with strands falling out, wearing cheap ill-fitting black office jacket, white blouse, plain dark skirt, walking slowly in office hallway holding documents, tired blank background expression"
]

for i, scene in enumerate(SCENES, 1):
    seed = random.randint(100000000, 999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, (Realistic, photorealistic:1.3), ultra detailed, "
              f"{scene}")
    prefix = f"kinoshita_v5_cfg{CFG}_s{seed}_{i:02d}"

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
