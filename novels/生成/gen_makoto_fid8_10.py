"""誠24歳: FaceID 0.8 本生成 10枚（スーツ5 + 私服5）"""
import requests, json, time, urllib.request, os, random

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR_NAME = "makoto"
AGE = "24"
MODEL_NAME = "yayoi_mix"
FID = "fid8"
FID_W = 0.8
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\01_24歳_社会人\採用"
os.makedirs(OUT, exist_ok=True)

REF_IMG = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\01_24歳_社会人\採用\makoto_24_yayoi_mix_s1193774_sidepart_a4_00001_.png"

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, jewelry, earring, necklace, "
       "glasses, spectacles, eyewear, "
       "beard, stubble, facial hair, "
       "younger than 20, teenager, "
       "feminine, woman, female features, androgynous, "
       "soft face, delicate, pretty, girly, effeminate, ambiguous gender, "
       "curly hair, wavy hair, colored hair, long hair, "
       "pompadour, quiff, slicked back, heavy wax, excessive volume, "
       "sharp sideburns, host style, flashy hair, gel hair, spiky hair, "
       "extreme two block, undercut")

HAIR = ("natural side parted short hair, 70-30 side part, "
        "late 2000s japanese salaryman hairstyle, conservative professional")

VARIANTS = [
    # (tag, clothes, pose, expr, detail)
    # === SUIT (5) ===
    ("suit_front",
     "navy suit, white dress shirt, dark red tie",
     "front view, standing in office, hands at sides, looking at camera",
     "calm steady expression",
     "office hallway, fluorescent light, modern japanese office"),
    ("suit_desk",
     "white shirt, navy suit jacket visible behind, tie loosened",
     "three-quarter angle, sitting at desk, looking at papers",
     "focused analytical expression",
     "desk with financial reports, office afternoon"),
    ("suit_profile",
     "navy suit, red tie, briefcase",
     "profile view, walking through corridor, mid-stride",
     "determined neutral expression",
     "bright office corridor, glass walls"),
    ("suit_window",
     "navy suit, white shirt, red tie",
     "side view, standing by window, one hand in pocket",
     "thoughtful contemplative expression",
     "floor-to-ceiling window, city view, daytime"),
    ("suit_meeting",
     "navy suit, white shirt, red tie",
     "sitting at conference table, hands clasped, looking up",
     "attentive listening expression",
     "meeting room, notepad, glass of water"),
    # === CASUAL (5) ===
    ("home_sofa",
     "simple white t-shirt, casual dark pants",
     "sitting on sofa, leaning back, looking at phone",
     "relaxed tired expression",
     "living room, evening lamp, bookshelf"),
    ("cafe_window",
     "white button-up shirt, no tie, casual jacket off",
     "three-quarter angle, sitting at cafe table with coffee",
     "slightly tired relaxed expression",
     "urban cafe, afternoon, window light"),
    ("street_walk",
     "navy overcoat, scarf, no suit visible",
     "walking on street, hands in pockets, looking ahead",
     "neutral commute expression",
     "city street, winter, overcast"),
    ("desk_home",
     "casual button-up shirt, rolled sleeves, no tie",
     "sitting at desk, looking at dual monitors",
     "intense analytical focus",
     "home office, stock charts on screen, late night"),
    ("kitchen_morning",
     "white t-shirt, casual pants",
     "standing in kitchen, pouring coffee, looking aside",
     "sleepy morning expression",
     "kitchen, morning light, coffee maker"),
]

def upload_ref():
    with open(REF_IMG, "rb") as f:
        try:
            r = requests.post(f"{BASE}/upload/image", files={"image": ("makoto_ref_24.png", f, "image/png")}, timeout=30)
            r.raise_for_status()
            return r.json()["name"]
        except Exception as e:
            print(f"Upload failed: {e}")
            return None

def gen_one(seed, prompt, neg, ref_name, prefix):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0], "clip":["1",1], "lora_name":LORA1, "strength_model":L1S, "strength_clip":L1S}},
        "3": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["2",0], "preset":"FACEID PLUS V2", "lora_strength":0.5, "provider":"CPU"}},
        "4": {"class_type": "LoadImage", "inputs": {"image": ref_name}},
        "5": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU", "model_name":"buffalo_l"}},
        "6": {"class_type": "IPAdapterFaceID", "inputs": {
            "model":["3",0], "ipadapter":["3",1], "image":["4",0],
            "weight":FID_W, "weight_faceidv2":0.0,
            "weight_type":"linear", "combine_embeds":"concat",
            "start_at":0.0, "end_at":1.0, "embeds_scaling":"V only",
            "insightface":["5",0]
        }},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip":["2",1]}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["2",1]}},
        "9": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "10": {"class_type": "KSampler", "inputs": {
            "seed":seed,"steps":STEPS,"cfg":CFG,
            "sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,
            "model":["6",0], "positive":["8",0], "negative":["7",0], "latent_image":["9",0]
        }},
        "11": {"class_type": "VAEDecode", "inputs": {"samples":["10",0], "vae":["1",2]}},
        "12": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix, "images":["11",0]}},
    }
    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status()
        pid = r.json()["prompt_id"]
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

print("Uploading reference...")
ref_name = upload_ref()
if not ref_name:
    print("ABORT"); exit(1)

print("10 variants (suit=5, casual=5)...")
base = f"(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, 24 year old japanese man, mid 20s, salaryman, masculine face, strong jawline, sharp features, no glasses, {HAIR}"
for i, (tag, clothes, pose, expr, detail) in enumerate(VARIANTS, 1):
    seed = random.randint(1000000000, 9999999999)
    prompt = f"{base}, {clothes}, {pose}, {expr}, {detail}"
    prefix = f"{CHAR_NAME}_{AGE}_{MODEL_NAME}_{FID}_s{seed}_{tag}"
    print(f"[{i}/10] s{seed} {tag}")
    gen_one(seed, prompt, NEG, ref_name, prefix)
    time.sleep(0.5)
print("完了。")
