"""
Test dual IPAdapter: FaceID (s5977) + Style (cardigan_sofa hair)
"""
import requests, json, time, os, urllib.parse, glob

BASE = "http://100.112.59.35:18188"

# Find files using glob to avoid manual path encoding issues
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
novels_dir = os.path.join(os.path.dirname(base_dir), "novels")

# Find face reference
face_matches = glob.glob(os.path.join(novels_dir, "**", "yuriko_face_s5977_00001_.png"), recursive=True)
FACE_REF = face_matches[0] if face_matches else None

# Find hair reference
hair_matches = glob.glob(os.path.join(novels_dir, "**", "yuriko_20_yayoi_mix_s3514249005_cardigan_sofa_00001_.png"), recursive=True)
HAIR_REF = hair_matches[0] if hair_matches else None

OUT = os.path.dirname(HAIR_REF) if HAIR_REF else None

print(f"FACE_REF: {FACE_REF}")
print(f"HAIR_REF: {HAIR_REF}")
print(f"OUT: {OUT}")

if not FACE_REF or not HAIR_REF:
    print("ERROR: Could not find reference images")
    exit(1)

os.makedirs(OUT, exist_ok=True)

NEG = "EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), hair above shoulders, bob cut, chin-length, long hair past shoulders"
POS = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
       "japanese young woman, 20 years old, newly married, gentle peaceful expression, "
       "plain natural face, minimal makeup, "
       "hair exactly ends at shoulders, not shorter not longer, straight black hair, "
       "simple beige one-piece dress, white sneakers, small shoulder bag, "
       "walking on street, spring afternoon, gentle breeze")

# Upload both images
for label, path in [("face", FACE_REF), ("hair", HAIR_REF)]:
    fname = os.path.basename(path)
    with open(path, "rb") as f:
        r = requests.post(f"{BASE}/upload/image", files={"image": (fname, f, "image/png")}, timeout=30)
    print(f"Upload {label}: {r.status_code} {r.json()}")
    if r.status_code != 200:
        exit()

wf = {
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "yayoi_mix.safetensors"}},
    "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0], "clip":["1",1], "lora_name":"JapaneseDollLikeness_v15.safetensors", "strength_model":0.5, "strength_clip":0.5}},
    "3": {"class_type": "LoraLoader", "inputs": {"model":["2",0], "clip":["2",1], "lora_name":"DetailTweaker.safetensors", "strength_model":0.2, "strength_clip":0.2}},
    "4": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["3",0], "preset":"FACEID PLUS V2", "lora_strength":0.5, "provider":"CPU"}},
    "5": {"class_type": "LoadImage", "inputs": {"image": "yuriko_face_s5977_00001_.png"}},
    "6": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU", "model_name":"buffalo_l"}},
    "7": {"class_type": "IPAdapterFaceID", "inputs": {"model":["4",0], "ipadapter":["4",1], "image":["5",0], "weight":0.8, "weight_faceidv2":0.0, "weight_type":"linear", "combine_embeds":"concat", "start_at":0.0, "end_at":1.0, "embeds_scaling":"V only", "insightface":["6",0]}},
    "8": {"class_type": "IPAdapterUnifiedLoader", "inputs": {"model":["7",0], "preset":"STANDARD (medium strength)"}},
    "9": {"class_type": "LoadImage", "inputs": {"image": os.path.basename(HAIR_REF)}},
    "10": {"class_type": "IPAdapter", "inputs": {"model":["8",0], "ipadapter":["8",1], "image":["9",0], "weight":0.25, "start_at":0.0, "end_at":1.0, "weight_type":"standard"}},
    "11": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip":["3",1]}},
    "12": {"class_type": "CLIPTextEncode", "inputs": {"text": POS, "clip":["3",1]}},
    "13": {"class_type": "EmptyLatentImage", "inputs": {"width":512,"height":768,"batch_size":1}},
    "14": {"class_type": "KSampler", "inputs": {"seed":42,"steps":28,"cfg":7.0,"sampler_name":"dpmpp_2m","scheduler":"karras","denoise":1.0,"model":["10",0], "positive":["12",0], "negative":["11",0], "latent_image":["13",0]}},
    "15": {"class_type": "VAEDecode", "inputs": {"samples":["14",0], "vae":["1",2]}},
    "16": {"class_type": "SaveImage", "inputs": {"filename_prefix":"test_dual_ipadapter", "images":["15",0]}},
}

r = requests.post(f"{BASE}/prompt", json={"prompt":wf})
print(f"Submit: {r.status_code}")
if r.status_code == 200:
    pid = r.json()["prompt_id"]
    print(f"ID: {pid}")
    for j in range(300):
        time.sleep(2)
        h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
        if pid in h:
            st = h[pid]["status"]["status_str"]
            if st == "success":
                print("SUCCESS")
                for nid, node in h[pid]["outputs"].items():
                    for img in node.get("images",[]):
                        params = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img["subfolder"], "type": img["type"]})
                        url = f"{BASE}/view?{params}"
                        outpath = os.path.join(OUT, img["filename"])
                        resp = requests.get(url, timeout=60)
                        with open(outpath, "wb") as f:
                            f.write(resp.content)
                        print(f"  Saved: {img['filename']} ({len(resp.content)//1024}kb)")
                break
            elif st == "error":
                msg = h[pid]["status"]["messages"][-1][1].get("exception_message", "unknown")
                print(f"ERROR: {msg}")
                break
else:
    print(f"ERR: {r.text[:1000]}")
