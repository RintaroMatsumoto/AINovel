"""伊藤・井上・木下: FaceID 各10枚 計30枚"""
import requests, json, time, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "majicMIX.safetensors"
W, H, STEPS, CFG = 512, 768, 30, 8.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
BASE_DIR = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像"

NEG = ("(worst quality:1.4), (low quality:1.4), EasyNegative, badhandv4, "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "mutated hands, extra hands, bad hands, "
       "beautiful, pretty, cute, attractive, gorgeous, "
       "handsome, model, actress, celebrity, "
       "elegant, stylish, trendy, fashionable, chic, "
       "makeup, lipstick, blush, eyeshadow, "
       "young, youthful, fresh, radiant, "
       "smiling, laughing, happy, cheerful, "
       "t-shirt, hoodie, jeans, casual, "
       "distinctive, memorable, outstanding")

CHARACTERS = [
    ("伊藤\\01_35歳_経理課", "ito_fid", "japanese salaryman, 35 years old, average office worker, tired, navy suit, white shirt, tie",
     ["sitting at desk, looking at computer monitor, office, tired expression",
      "standing by water cooler, holding cup, casual office conversation",
      "walking in hallway with documents, office corridor, mid-stride",
      "portrait, office background, tired salaryman, neutral expression",
      "sitting at meeting table, listening, boring meeting face",
      "standing at office entrance, holding briefcase, about to leave",
      "at desk, talking on phone, hand on forehead, tired",
      "in break room, drinking coffee, staring into space",
      "at desk, organizing papers, focused but tired, office",
      "portrait, half body, navy suit, blank office expression"]),
    ("井上\\01_28歳_経理課", "inoue_fid", "japanese office lady, 28 years old, plain average woman, glasses, office wear",
     ["sitting at desk, typing on keyboard, glasses, office background",
      "standing at filing cabinet, holding folder, reading, glasses",
      "walking in hallway, carrying documents, office lady, glasses",
      "portrait, office background, plain office lady, tired eyes",
      "sitting at meeting table, taking notes, glasses, boring expression",
      "at desk, looking at monitor, tired office lady, glasses",
      "in office kitchen, pouring tea, plain expression, glasses",
      "standing by window, looking at phone, break time, glasses",
      "at desk, organizing document piles, busy office lady, glasses",
      "portrait, half body, navy blazer, glasses, neutral expression"]),
    ("木下\\01_30代_経理課", "kinoshita_fid", "japanese office woman, mid 30s, plain tired face, overweight, office clothes",
     ["sitting at desk with many papers, typing, tired heavy expression",
      "standing by filing cabinet with thick folder, overweight, tired",
      "walking slowly in hallway with documents, tired plump body",
      "portrait, desk background with papers, tired plain office woman",
      "sitting at cubicle surrounded by document stacks, exhausted look",
      "at desk, reading document with tired eyes, piles of papers",
      "in office, carrying box of files, tired expression, plump",
      "standing at photocopier, copying papers, blank tired expression",
      "sitting at desk, head in hands briefly, overwhelmed, tired",
      "portrait, half body, navy blazer, tired plain office woman"]),
]

def upload_ref(path):
    with open(path, "rb") as f:
        r = requests.post(f"{BASE}/upload/image", files={"image": ("ref.png", f, "image/png")}, timeout=30)
    return r.json()["name"]

for folder, tag, base_desc, scenes in CHARACTERS:
    out_dir = os.path.join(BASE_DIR, folder)
    ref_path = os.path.join(out_dir, "採用", [f for f in os.listdir(os.path.join(out_dir, "採用")) if f.endswith('.png')][0])
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n=== {tag}: uploading ref ===")
    ref_name = upload_ref(ref_path)
    print(f"  Ref: {os.path.basename(ref_path)}")

    for i, scene in enumerate(scenes, 1):
        seed = random.randint(100000000, 999999999)
        prompt = (f"(masterpiece, best quality:1.2), 8k, (Realistic, photorealistic:1.3), ultra detailed, "
                  f"{base_desc}, {scene}")
        prefix = f"{tag}_cfg{CFG}_s{seed}_{i:02d}"

        wf = {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
            "2": {"class_type": "CLIPSetLastLayer", "inputs": {"clip":["1",1], "stop_at_clip_layer":-2}},
            "3": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["1",0],"preset":"FACEID PLUS V2","lora_strength":0.5,"provider":"CPU"}},
            "4": {"class_type": "LoadImage", "inputs": {"image": ref_name}},
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
                                outpath = os.path.join(out_dir, img["filename"])
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

print("\n完了。全30枚生成。")
