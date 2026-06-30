"""誠40歳: 白髪・メガネ・短髪 強調テスト 10枚"""
import requests, json, time, urllib.request, os, random

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "DetailTweaker.safetensors", 0.2
W, H, STEPS = 512, 768, 28
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR_NAME = "makoto"
AGE = "40"
MODEL_NAME = "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\02_40歳_探索"
os.makedirs(OUT, exist_ok=True)

REF_IMG = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\01_24歳_社会人\採用\makoto_24_yayoi_mix_s1193774_sidepart_a4_00001_.png"

# Negative WITHOUT glasses removal — we WANT glasses now
NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, jewelry, earring, necklace, "
       "feminine, woman, female features, androgynous, "
       "soft face, delicate, pretty, girly, effeminate, ambiguous gender, "
       "younger than 20, teenager, "
       "curly hair, wavy hair, colored hair, long hair, "
       "pompadour, quiff, slicked back, heavy wax, excessive volume, "
       "sharp sideburns, host style, flashy hair, gel hair, spiky hair, "
       "extreme two block, undercut, "
       "beard, full beard, long stubble")

BASE_POS = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
            "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
            "japanese man, in his 40s, salaryman, "
            "masculine face, strong jawline, sharp features")

VARIANTS = [
    # (tag, fid_w, cfg, aging_hair, glasses, clothes_pose)
    # === 白髪強調 (4) ===
    ("saltpepper_strong", 0.4, 9.5,
     "short natural side part, (gray salt and pepper hair:1.4), white temples, silver mixed natural hair, aging hair",
     "no glasses",
     "navy suit, white shirt, red tie, front view, standing in office, looking at camera, calm experienced expression"),
    ("saltpepper_tired", 0.4, 10.0,
     "short neat haircut, (heavy gray salt and pepper hair:1.5), prominent white temples, gray streaks",
     "no glasses",
     "white shirt, loosened tie, sitting at desk, looking at papers, tired eyes, crow's feet"),
    ("saltpepper_profile", 0.3, 10.0,
     "short side part, (gray hair:1.4), white at temples, salt and pepper all over, natural gray",
     "no glasses",
     "navy suit, profile view, walking, tired determined expression, dark circles"),
    ("saltpepper_smile", 0.5, 9.0,
     "short neat gray black hair, (salt and pepper:1.3), silver temples, graying",
     "no glasses",
     "white shirt, vest, sitting in cafe, reading newspaper, calm content expression"),
    # === メガネ (4) ===
    ("glasses_silver", 0.5, 9.0,
     "short salt and pepper hair, neat side part",
     "(silver metal frame glasses:1.2), thin wire glasses, subtle professional eyewear",
     "navy suit, white shirt, red tie, front view, standing, professional serious expression"),
    ("glasses_reading", 0.4, 9.5,
     "short gray black hair, conservative haircut",
     "(black frame reading glasses:1.2), semi-rimless, worn while looking at documents",
     "white shirt, no tie, sleeves rolled, sitting at desk, looking at financial report, focused expression"),
    ("glasses_window", 0.4, 9.5,
     "short natural gray hair, side part",
     "(silver frame glasses:1.2), thin metal glasses, business style",
     "navy suit jacket, standing by window, looking outside, thoughtful tired expression"),
    ("glasses_broken", 0.3, 10.0,
     "messy gray stubble hair, disheveled",
     "(silver glasses slightly askew:1.1), glasses on tired face",
     "wrinkled white shirt, untucked, sitting in dim room, hollow exhausted eyes, stubble"),
    # === 短髪 (2) ===
    ("buzzcut_suit", 0.4, 9.5,
     "(very short cropped hair:1.3), short buzzed sides, short top, military style short haircut, no side part",
     "no glasses",
     "navy suit, white shirt, red tie, front view, standing, serious stern expression"),
    ("buzzcut_casual", 0.5, 9.0,
     "(very short buzzed hair:1.3), close cropped all over, short stubble hair, practical short haircut",
     "no glasses",
     "white t-shirt, casual jacket, standing on street, looking at phone, neutral expression"),
]

def upload_ref():
    with open(REF_IMG, "rb") as f:
        try:
            r = requests.post(f"{BASE}/upload/image", files={"image": ("makoto_ref_24.png", f, "image/png")}, timeout=30)
            r.raise_for_status()
            return r.json()["name"]
        except Exception as e:
            print(f"Upload failed: {e}"); return None

def gen_one(seed, prompt, neg, ref_name, prefix, fid_w, cfg):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0], "clip":["1",1], "lora_name":LORA1, "strength_model":L1S, "strength_clip":L1S}},
        "3": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["2",0], "preset":"FACEID PLUS V2", "lora_strength":0.5, "provider":"CPU"}},
        "4": {"class_type": "LoadImage", "inputs": {"image": ref_name}},
        "5": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU", "model_name":"buffalo_l"}},
        "6": {"class_type": "IPAdapterFaceID", "inputs": {
            "model":["3",0], "ipadapter":["3",1], "image":["4",0],
            "weight":fid_w, "weight_faceidv2":0.0,
            "weight_type":"linear", "combine_embeds":"concat",
            "start_at":0.0, "end_at":1.0, "embeds_scaling":"V only",
            "insightface":["5",0]
        }},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip":["2",1]}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["2",1]}},
        "9": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "10": {"class_type": "KSampler", "inputs": {
            "seed":seed,"steps":STEPS,"cfg":cfg,
            "sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,
            "model":["6",0], "positive":["8",0], "negative":["7",0], "latent_image":["9",0]
        }},
        "11": {"class_type": "VAEDecode", "inputs": {"samples":["10",0], "vae":["1",2]}},
        "12": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix, "images":["11",0]}},
    }
    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status(); pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  {prefix} SUBMIT: {e}"); return
    for j in range(120):
        time.sleep(2)
        try:
            h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
            if pid in h:
                if h[pid]["status"]["status_str"] == "success":
                    for nid, node in h[pid]["outputs"].items():
                        for img in node.get("images",[]):
                            url = f"{BASE}/view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
                            out = os.path.join(OUT, img["filename"])
                            urllib.request.urlretrieve(url, out)
                            print(f"  {prefix} OK ({os.path.getsize(out)//1024}kb)")
                    return
                elif h[pid]["status"]["status_str"] == "error":
                    print(f"  {prefix} ERROR"); return
        except:
            if j == 119: print(f"  {prefix} TIMEOUT")

print("Uploading reference (24yo Makoto)...")
ref_name = upload_ref()
if not ref_name: print("ABORT"); exit(1)

print("10 variations (white hair / glasses / short hair)...")
for i, (tag, fid_w, cfg, hair, glasses, scene) in enumerate(VARIANTS, 1):
    seed = random.randint(1000000000, 9999999999)
    prompt = f"{BASE_POS}, {hair}, {glasses}, {scene}"
    prefix = f"{CHAR_NAME}_{AGE}_{MODEL_NAME}_fid{int(fid_w*10)}_cfg{int(cfg)}_s{seed}_{tag}"
    print(f"[{i}/10] {tag} fid{int(fid_w*10)} cfg{int(cfg)}")
    gen_one(seed, prompt, NEG, ref_name, prefix, fid_w, cfg)
    time.sleep(0.5)
print("完了。")
