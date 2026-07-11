"""伊藤・井上・木下 v2: ブサイク厳守"""
import requests, json, time, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "majicMIX.safetensors"
W, H, STEPS, CFG = 512, 768, 30, 8.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
BASE_DIR = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像"

NEG = ("(worst quality:1.4), (low quality:1.4), EasyNegative, badhandv4, "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "mutated hands, extra hands, bad hands, deformed hands, "
       "handsome, beautiful, pretty, cute, attractive, gorgeous, "
       "model, fashion model, actor, actress, celebrity, "
       "charming, sexy, alluring, elegant, stylish, trendy, "
       "makeup, lipstick, blush, eyeshadow, mascara, eyeliner, "
       "young, youthful, fresh face, clear skin, radiant, "
       "cool, sharp, angular, defined jaw, chiseled, "
       "slim, slender, fit, athletic, toned, "
       "smiling, laughing, happy, cheerful, bright, "
       "fashionable clothes, trendy outfit, designer, brand")

CHARACTERS = [
    ("伊藤\\01_35歳_経理課", "ito",
     "japanese man, 35 years old, salaryman, fat belly, double chin, average ugly face, tired dull eyes, receding hairline, white collar shirt untucked, slouching posture, office worker, plain",
     ["sitting at messy office desk, staring at monitor with dull expression, cheap navy suit jacket on chair back, tired",
      "standing by water cooler, holding paper cup, pot belly visible, cheap wrinkled shirt, office background",
      "portrait, fat middle-aged salaryman, double chin, tired bloodshot eyes, receding hairline, cheap tie loosened, office",
      "sitting at desk, leaning back in chair, hand on belly, boring meeting expression, disheveled shirt",
      "walking in office corridor with slow tired pace, overweight, cheap suit, untucked shirt, carrying documents"]),
    ("井上\\01_28歳_経理課", "inoue",
     "japanese woman, 28 years old, office lady, ugly plain face, tired eyes, pale skin, thin limp hair, skinny flat body, no curves, no makeup unattractive, boring office lady",
     ["sitting at desk, staring blankly at computer, tired plain face, limp hair, cheap plain blouse, messy desk with papers",
      "standing in office, holding documents, dull expression, ugly plain face, cheap office wear, glasses, pale tired look",
      "portrait, ugly office lady, plain unattractive face, tired pale skin, bad skin complexion, cheap blouse, office background",
      "sitting in meeting, looking down at notepad, boring tired expression, ugly plain face, cheap office clothes",
      "walking in hallway, carrying file box, plain ugly face, no makeup tired look, cheap work clothes, hunching slightly"]),
    ("木下\\01_30代_経理課", "kinoshita",
     "japanese woman, mid 30s, office lady, older tired face, ugly plain, overweight, double chin, bad skin, cheap messy hair, no fashion, no makeup",
     ["sitting at overflowing desk with piles of documents, tired face, overweight, cheap plain blouse, office, exhausted",
      "standing by filing cabinet, holding thick folder, fat overweight body, plain ugly face, tired eyes, messy plain clothes",
      "portrait, 35 year old ugly office woman, overweight, double chin, tired dull eyes, cheap blouse, messy hair, desk papers background",
      "sitting at cubicle surrounded by document stacks, tired exhausted expression, plain face, overweight, cheap work clothes",
      "walking slowly in office, carrying heavy stack of files, tired stooped posture, plain ugly face, cheap clothes"]),
]

for folder, tag, base_desc, scenes in CHARACTERS:
    out_dir = os.path.join(BASE_DIR, folder)
    os.makedirs(out_dir, exist_ok=True)
    print(f"\n=== {tag} 5枚 ===")
    for i, scene in enumerate(scenes, 1):
        seed = random.randint(100000000, 999999999)
        prompt = (f"(masterpiece, best quality:1.2), 8k, (Realistic, photorealistic:1.3), ultra detailed, "
                  f"{base_desc}, {scene}")
        prefix = f"{tag}_v2_cfg{CFG}_s{seed}_{i:02d}"

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
                                outpath = os.path.join(out_dir, img["filename"])
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

print("\n完了。全15枚。")
