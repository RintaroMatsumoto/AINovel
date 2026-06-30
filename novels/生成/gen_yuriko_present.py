"""
百合子34歳（現在・主婦）: FaceIDのみで叩き生成
髪は背中中ほどまでのばした黒髪。年齢をプロンプトで表現。
後でDual IPAdapterで仕上げる前提。
"""
import requests, json, time, os, random, urllib.parse, glob

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "JapaneseDollLikeness_v15.safetensors", 0.5
LORA2, L2S = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR_NAME = "yuriko"
AGE = "34"
MODEL_NAME = "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\01_34歳_現在_主婦"
os.makedirs(OUT, exist_ok=True)

novels_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "novels")
face_matches = glob.glob(os.path.join(novels_dir, "**", "yuriko_face_s5977_00001_.png"), recursive=True)
REF_IMG = face_matches[0] if face_matches else None
if not REF_IMG:
    print("ERROR: face reference not found")
    exit(1)

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, ribbon, curly hair, wavy hair, "
       "young, teenager, 20s, fresh face, firm skin, smooth skin, perfect skin, "
       "bangs, bob cut, shoulder-length, hair ends at shoulders, "
       "long hair past waist, very long hair")

BASE_FACE = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
             "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
             "japanese woman, 34 years old, mother of two, married, mature beauty, "
             "plain natural face, no makeup, realistic skin texture, "
             "subtle fine lines around eyes, slight dark circles under eyes, "
             "tired gentle eyes, carries weight of years, "
             "natural aging signs, mature facial structure")

HAIR = ("long straight black hair, hair reaches middle of back, "
        "mid-back length straight hair, natural black hair")

VARIANTS = [
    # (name, hair_detail, clothes_pose)
    ("kitchen_apron",
     "long hair tied back loosely in a low ponytail",
     "simple house dress with apron, in kitchen, "
     "preparing dinner, turning to look aside, "
     "warm evening light, domestic quiet moment, slight tired smile"),
    ("sofa_distant",
     "long straight black hair, slightly disheveled",
     "plain comfortable home wear, sitting on sofa, "
     "gazing out window, distant unfocused look, evening, "
     "alone in living room, pensieve mood, soft lamp light"),
    ("laundry_veranda",
     "long hair pulled back casually",
     "simple t-shirt and knee-length skirt, on veranda, "
     "hanging laundry, afternoon sun, "
     "everyday routine, looking away, slight melancholy"),
    ("kids_entrance",
     "long hair, some strands loose",
     "casual home wear, at entrance hall, "
     "sending children off, gentle motherly smile, morning light, "
     "waving hand, warm expression despite tired eyes"),
    ("bedroom_desk",
     "long hair tied in loose bun, strands falling",
     "plain robe over nightgown, sitting at small desk, "
     "looking at household accounts, pen in hand, "
     "late night, concentrated but tired expression, desk lamp"),
    ("supermarket",
     "long straight black hair",
     "simple casual dress, light cardigan, shoulder bag, "
     "at supermarket, choosing vegetables, "
     "daytime, ordinary errand, neutral expression"),
    ("night_alone",
     "long hair down, slightly messy",
     "comfortable worn home wear, sitting at kitchen table, "
     "cup of tea in hands, staring into middle distance, "
     "late night, household asleep, exhausted vulnerable moment"),
    ("photo_memory",
     "long hair falling forward",
     "simple home clothes, sitting on floor by low table, "
     "holding an old photo album, looking down at photos, "
     "soft daytime light through window, complex bittersweet expression"),
    ("station_wait",
     "long hair, windblown slightly",
     "beige trench coat, simple scarf, "
     "waiting at train station, hands in pockets, "
     "overcast afternoon, standing alone, thoughtful look"),
    ("mirror_reflection",
     "long hair, mid-back visible",
     "simple undershirt, in bedroom, "
     "standing before dresser mirror, looking at own reflection, "
     "examining face, early morning, pensive intimate moment"),
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

def build_workflow(seed, prompt, neg, ref_name, prefix):
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
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": neg_esc, "clip":["3",1]}},
        "9": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt_esc, "clip":["3",1]}},
        "10": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "11": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["7",0], "positive":["9",0], "negative":["8",0], "latent_image":["10",0]}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples":["11",0], "vae":["1",2]}},
        "13": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix, "images":["12",0]}},
    }

def gen_one(seed, prompt, neg, ref_name, prefix):
    wf = build_workflow(seed, prompt, neg, ref_name, prefix)
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
print("Step 1/2: Uploading reference face...")
ref_name = upload_ref_image(REF_IMG)
if not ref_name:
    exit(1)

print("Step 2/2: Generating 10 variants (FaceID only, no hair ref)...")
for i, (name, hair_detail, clothes_pose) in enumerate(VARIANTS, 1):
    seed = random.randint(1000000000, 9999999999)
    prompt = f"{BASE_FACE}, {HAIR}, {hair_detail}, {clothes_pose}"
    prefix = f"{CHAR_NAME}_{AGE}_{MODEL_NAME}_s{seed}_{name}"
    print(f"[{i}/10] s{seed} {name}")
    gen_one(seed, prompt, NEG, ref_name, prefix)
    time.sleep(0.5)
