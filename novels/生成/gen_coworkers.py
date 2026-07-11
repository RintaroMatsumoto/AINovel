"""伊藤・井上・木下: majicMIX 各5枚 計15枚"""
import requests, json, time, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "majicMIX.safetensors"
W, H, STEPS, CFG = 512, 768, 30, 8.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
BASE_DIR = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像"
NEG = ("(worst quality:1.4), (low quality:1.4), EasyNegative, badhandv4, "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "mutated hands, extra hands, bad hands, deformed hands, "
       "fashionable, stylish, trendy, elegant, chic, model, "
       "handsome, beautiful, pretty, cute, attractive, "
       "makeup, lipstick, blush, eyeshadow, "
       "young, boyish, girly, "
       "smiling, laughing, happy, cheerful, "
       "kimono, wafuku, casual, t-shirt, hoodie, sportswear")

CHARACTERS = [
    # (folder, prefix, prompt_base, scenes)
    ("伊藤\\01_35歳_経理課", "ito",
     "japanese man, 35 years old, salaryman, ordinary average face, not handsome, plain, stocky build, short hair",
     ["sitting at office desk, front view, looking at computer monitor, navy suit, white shirt, tie, office background",
      "standing in office near desk, holding coffee cup, three-quarter view, navy suit, relaxed expression",
      "portrait, 35 year old japanese salaryman, plain face, short hair, stocky build, navy suit and tie, office",
      "sitting at desk, talking to colleague off-screen, gesturing with hand, friendly expression, office cubicle",
      "walking in office corridor, carrying documents, mid-stride, navy suit, briefcase, professional"]),
    # (folder, prefix, prompt_base, scenes)
    ("井上\\01_28歳_経理課", "inoue",
     "japanese woman, 28 years old, office lady, average plain face, not pretty, slender, short bob hair, glasses",
     ["sitting at office desk, typing on keyboard, front view, navy blazer, white blouse, office background",
      "standing at office filing cabinet, holding folder, three-quarter view, plain office wear, glasses",
      "portrait, 28 year old japanese office lady, plain face, short bob hair, glasses, navy blazer, office",
      "sitting at meeting table, listening, holding pen, office lady wear, glasses, professional expression",
      "walking in office hallway, holding documents, plain office clothes, glasses, carrying shoulder bag"]),
    # (folder, prefix, prompt_base, scenes)
    ("木下\\01_30代_経理課", "kinoshita",
     "japanese woman, mid 30s, office lady, plain average face, not attractive, ordinary, plain clothes, quiet expression",
     ["sitting at desk with many papers, working on documents, focused, plain office wear, glasses, office background",
      "standing by desk, holding file, looking down at papers, three-quarter view, plain blouse, skirt",
      "portrait, 35 year old japanese office lady, plain ordinary face, not pretty, desk with papers background",
      "sitting at desk in cubicle, surrounded by document stacks, working quietly, plain office clothes",
      "standing in office, reading document in hand, neutral expression, plain work attire, glasses"]),
]

def gen_batch(folder, tag, base_desc, scenes):
    out_dir = os.path.join(BASE_DIR, folder)
    os.makedirs(out_dir, exist_ok=True)
    for i, scene in enumerate(scenes, 1):
        seed = random.randint(100000000, 999999999)
        prompt = (f"(masterpiece, best quality:1.2), 8k, (Realistic, photorealistic:1.3), ultra detailed, "
                  f"{base_desc}, {scene}")
        prefix = f"{tag}_majic_cfg{CFG}_s{seed}_{i:02d}"

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
            print(f"  [{tag} {i}/5] SUBMIT: {e}"); continue

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
                                    print(f"  [{tag} {i}/5] OK ({len(resp.content)//1024}kb)")
                                else:
                                    print(f"  [{tag} {i}/5] TOOSMALL")
                        break
                    elif st == "error":
                        print(f"  [{tag} {i}/5] ERROR"); break
            except:
                if j == 299: print(f"  [{tag} {i}/5] TIMEOUT")
        time.sleep(0.3)

for folder, tag, base_desc, scenes in CHARACTERS:
    print(f"\n=== {tag} 5枚 ===")
    gen_batch(folder, tag, base_desc, scenes)

print("\n完了。全15枚生成。")
