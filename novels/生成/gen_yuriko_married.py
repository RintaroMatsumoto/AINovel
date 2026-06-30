"""
百合子20歳（結婚当初）:  Dual IPAdapter で顔＋髪型固定生成
FaceID (s5977) → 顔固定
IPAdapter (cardigan_sofa) → 髪型固定
妊娠あり3枚 + 妊娠なし7枚 = 10枚
"""
import requests, json, time, urllib.request, os, random, urllib.parse, glob

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "JapaneseDollLikeness_v15.safetensors", 0.5
LORA2, L2S = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR_NAME = "yuriko"
AGE = "20"
MODEL_NAME = "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\03_20歳_結婚当初"
os.makedirs(OUT, exist_ok=True)

# Find reference images via glob
novels_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "novels")
face_matches = glob.glob(os.path.join(novels_dir, "**", "yuriko_face_s5977_00001_.png"), recursive=True)
hair_matches = glob.glob(os.path.join(novels_dir, "**", "yuriko_20_yayoi_mix_s3514249005_cardigan_sofa_00001_.png"), recursive=True)
REF_IMG = face_matches[0] if face_matches else None
HAIR_REF = hair_matches[0] if hair_matches else None

if not REF_IMG:
    print("ERROR: face reference not found")
    exit(1)
if not HAIR_REF:
    print("ERROR: hair reference not found (need cardigan_sofa image)")
    exit(1)

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "makeup, frills, lace, ribbon, curly hair, wavy hair, "
       "long hair, long ponytail, hair past shoulders, "
       "hair above shoulders, bob cut, chin-length")

BASE_FACE = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
             "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
             "japanese young woman, 20 years old, newly married, gentle peaceful expression, "
             "plain natural face, minimal makeup")

HAIR = "shoulder-length straight black hair, hair ends at shoulders, exactly shoulder length"

VARIANTS = [
    # (name, hair_detail, clothes_pose)
    ("apron_back",
     "shoulder-length hair tied back loosely, a few strands at temples",
     "white blouse, beige apron tied at waist, home wear, "
     "in small kitchen, turning back looking over shoulder, natural daylight, "
     "warm cozy atmosphere, slight smile"),
    ("cardigan_sofa",
     "shoulder-length straight black hair",
     "soft cream cardigan, simple home dress, "
     "sitting on sofa, reading a book, legs curled up, "
     "living room, afternoon sunlight, relaxed peaceful vibe"),
    ("simple_dress_walk",
     "shoulder-length straight black hair",
     "simple beige one-piece dress, white sneakers, small shoulder bag, "
     "walking on street, shopping bag in hand, "
     "spring afternoon, gentle breeze, looking slightly away"),
    ("sweater_window",
     "shoulder-length hair, slightly tucked behind ears",
     "thin knit sweater in light gray, casual home pants, "
     "standing by window, looking outside thoughtfully, "
     "soft morning light, contemplative mood"),
    ("casual_veranda",
     "shoulder-length hair pulled into low loose ponytail",
     "loose-fit t-shirt and comfortable knee-length skirt, "
     "on veranda, leaning on railing, back view slightly turning face, "
     "evening golden hour, wind in hair"),
    ("clean_home",
     "shoulder-length hair tied with simple cloth band",
     "simple white t-shirt, light blue knee-length skirt, barefoot, "
     "in living room, holding cleaning cloth, bending slightly, "
     "bright daylight, candid everyday moment, natural smile"),
    ("spring_coat",
     "shoulder-length straight black hair",
     "light beige spring trench coat, white scarf, "
     "waiting at station area, looking at watch, "
     "early spring, cloudy sky, slightly chilly atmosphere"),
    ("maternity_side",
     "shoulder-length hair, slightly tousled",
     "loose maternity one-piece dress in soft navy, "
     "late pregnancy, standing by window, hand on belly, "
     "side view, profile, gentle expectant look"),
    ("maternity_sofa",
     "shoulder-length hair, some strands loose",
     "stretchy knit top, soft maternity leggings, oversized cardigan, "
     "sitting on sofa, resting, both hands on pregnant belly, "
     "front view, peaceful content expression, soft lamplight"),
    ("maternity_bedroom",
     "shoulder-length hair pulled back gently",
     "loose-fitting nightgown, thin robe over shoulders, "
     "in bedroom, sitting on edge of bed, looking down at belly, "
     "early morning light through curtain, quiet intimate moment"),
]

def upload_ref_image(path):
    with open(path, "rb") as f:
        r = requests.post(f"{BASE}/upload/image", files={"image": (os.path.basename(path), f, "image/png")}, timeout=30)
    if r.status_code == 200:
        name = r.json()["name"]
        print(f"Upload OK: {name}")
        return name
    print(f"Upload FAIL: {r.status_code}")
    return None

def build_workflow(seed, prompt, neg, ref_name, prefix, hair_ref_name):
    neg_esc = neg.replace('"', '\\"')
    prompt_esc = prompt.replace('"', '\\"')
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name":CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0], "clip":["1",1], "lora_name":LORA1, "strength_model":L1S, "strength_clip":L1S}},
        "3": {"class_type": "LoraLoader", "inputs": {"model":["2",0], "clip":["2",1], "lora_name":LORA2, "strength_model":L2S, "strength_clip":L2S}},
        "4": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["3",0], "preset":"FACEID PLUS V2", "lora_strength":0.5, "provider":"CPU"}},
        "5": {"class_type": "LoadImage", "inputs": {"image": ref_name}},
        "6": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU", "model_name":"buffalo_l"}},
        "7": {"class_type": "IPAdapterFaceID", "inputs": {"model":["4",0], "ipadapter":["4",1], "image":["5",0], "weight":0.8, "weight_faceidv2":0.0, "weight_type":"linear", "combine_embeds":"concat", "start_at":0.0, "end_at":1.0, "embeds_scaling":"V only", "insightface":["6",0]}},
        "8": {"class_type": "IPAdapterUnifiedLoader", "inputs": {"model":["7",0], "preset":"STANDARD (medium strength)"}},
        "9": {"class_type": "LoadImage", "inputs": {"image": hair_ref_name}},
        "10": {"class_type": "IPAdapter", "inputs": {"model":["8",0], "ipadapter":["8",1], "image":["9",0], "weight":0.25, "start_at":0.0, "end_at":1.0, "weight_type":"standard"}},
        "11": {"class_type": "CLIPTextEncode", "inputs": {"text": neg_esc, "clip":["3",1]}},
        "12": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt_esc, "clip":["3",1]}},
        "13": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "14": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["10",0], "positive":["12",0], "negative":["11",0], "latent_image":["13",0]}},
        "15": {"class_type": "VAEDecode", "inputs": {"samples":["14",0], "vae":["1",2]}},
        "16": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix, "images":["15",0]}},
    }

def gen_one(seed, prompt, neg, ref_name, prefix, hair_ref_name):
    wf = build_workflow(seed, prompt, neg, ref_name, prefix, hair_ref_name)
    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status()
        pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  {prefix} SUBMIT: {e}")
        return
    for j in range(300):
        time.sleep(2)
        try:
            h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
            if pid in h:
                st = h[pid]["status"]["status_str"]
                if st == "success":
                    for nid, node in h[pid]["outputs"].items():
                        for img in node.get("images",[]):
                            params = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img["subfolder"], "type": img["type"]})
                            url = f"{BASE}/view?{params}"
                            outpath = os.path.join(OUT, img["filename"])
                            resp = requests.get(url, timeout=60)
                            with open(outpath, "wb") as f:
                                f.write(resp.content)
                            print(f"  {prefix} OK ({len(resp.content)//1024}kb)")
                    return
                elif st == "error":
                    print(f"  {prefix} ERROR")
                    return
        except:
            if j == 299:
                print(f"  {prefix} TIMEOUT")
                return

# === MAIN ===
print("Step 1/2: Uploading reference images...")
ref_name = upload_ref_image(REF_IMG)
if not ref_name:
    print("ABORT: face ref upload failed")
    exit(1)
hair_ref_name = upload_ref_image(HAIR_REF)
if not hair_ref_name:
    print("ABORT: hair ref upload failed")
    exit(1)

print("Step 2/2: Generating 10 variants (Dual IPAdapter)...")
for i, (name, hair_detail, clothes_pose) in enumerate(VARIANTS, 1):
    seed = random.randint(1000000000, 9999999999)
    prompt = f"{BASE_FACE}, {HAIR}, {hair_detail}, {clothes_pose}"
    prefix = f"{CHAR_NAME}_{AGE}_{MODEL_NAME}_s{seed}_{name}"
    pregnant_tag = " [PREG]" if "maternity" in name else ""
    print(f"[{i}/10] s{seed} {name}{pregnant_tag}")
    gen_one(seed, prompt, NEG, ref_name, prefix, hair_ref_name)
    time.sleep(0.5)
