"""
橘栞: IPAdapterFaceID で年齢別一括生成
参照: 確定済み hoodie_front_00002
14歳(6枚) + 3歳(4枚) + 16歳(6枚) = 16枚
"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "JapaneseDollLikeness_v15.safetensors", 0.5
LORA2, L2S = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR, MODEL = "shiori", "yayoi_mix"

REF = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘栞\03_13歳_中学生_誠seed\shiori_13_yayoi_mix_s1193774_casual_hoodie_front_00002_.png"
OUT_BASE = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘栞"

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "adult, mature, old, aging, wrinkles, "
       "heavy makeup, dark eyeshadow, lipstick, dyed hair, colored hair, "
       "blonde hair, brown hair, curly hair, wavy hair")

# ─── 14歳 ───
AGE14_DIR = os.path.join(OUT_BASE, "01_14歳_中学生")
os.makedirs(AGE14_DIR, exist_ok=True)

AGE14_VARIANTS = [
    ("school_front",
     "long straight black hair, neat bangs, hair behind ears, natural shine",
     "navy school blazer, white blouse, gray pleated skirt, navy ribbon, knee-high black socks, loafers",
     "front view, standing, facing camera, school gate, morning light, innocent expression"),
    ("school_threeq",
     "long straight black hair, neat bangs, low ponytail",
     "navy school blazer, white blouse, gray pleated skirt, navy ribbon, school bag",
     "three-quarter view, walking in school hallway, looking ahead"),
    ("school_desk",
     "long straight black hair, neat bangs, hair behind ears",
     "navy school blazer over chair visible, white blouse, ribbon loosened",
     "sitting at classroom desk, writing in notebook, concentrated, afternoon light"),
    ("home_dinner",
     "long straight black hair, casual, slightly messy from school",
     "white t-shirt, gray hoodie unzipped, comfortable home clothes",
     "sitting at dinner table, chopsticks in hand, happy family moment, warm lighting"),
    ("home_casual",
     "long straight black hair, messy bun",
     "oversized hoodie, sweatpants, comfortable loungewear",
     "sitting on living room sofa, phone in hand, relaxed, evening"),
    ("portrait_happy",
     "long straight black hair, neat bangs, hair behind ears",
     "white blouse, gray cardigan, school uniform style",
     "front portrait, smiling naturally, bright eyes, warm expression"),
]

# ─── 3歳 ───
AGE3_DIR = os.path.join(OUT_BASE, "02_3歳_幼児")
os.makedirs(AGE3_DIR, exist_ok=True)

AGE3_VARIANTS = [
    ("doll_hold",
     "short black hair, straight, baby bangs, round face, chubby cheeks",
     "cute child dress, floral pattern, white socks, mary jane shoes",
     "holding a vintage french doll in both arms, looking at it lovingly, indoors, warm light"),
    ("doll_discover",
     "short black hair, straight, baby bangs, round face, chubby cheeks",
     "simple home clothes, t-shirt and shorts",
     "sitting on floor, doll in lap, hands on doll's back, curious expression, discovering something"),
    ("portrait_smile",
     "short black hair, straight, baby bangs, round face, chubby cheeks",
     "cute pastel dress, white collar",
     "front view, standing, big innocent smile, looking at camera, bright daylight"),
    ("playful",
     "short black hair, straight, baby bangs, messy",
     "casual toddler clothes, colorful t-shirt, denim overalls",
     "playing in living room, looking up, laughing, happy child, sunlight from window"),
]

# ─── 16歳 ───
AGE16_DIR = os.path.join(OUT_BASE, "03_16歳_地雷系")
os.makedirs(AGE16_DIR, exist_ok=True)

AGE16_VARIANTS = [
    ("jirai_stand",
     "long black hair, face-framing curls (yoshinmori style), thick bangs",
     "white fake fur coat, black frill blouse, pleated mini skirt, patterned tights, platform boots",
     "standing on street at night, neon lights in background, kabukicho, cautious defensive expression"),
    ("jirai_profile",
     "long black hair, yoshinmori curls, twin tail half-up",
     "white fake fur coat, frill blouse, mini skirt",
     "side view, standing on street corner, looking away, night, lonely atmosphere"),
    ("jirai_front",
     "long black hair, thick bangs, loose waves, pink hair clip",
     "black oversized sweater, plaid skirt, MCM backpack, platform sneakers",
     "front view, standing, arms crossed, forced tough expression, street background"),
    ("trade_focus",
     "long black hair tied back, simple, minimal makeup, sharp eyes",
     "black hoodie, no makeup look, focused intense expression",
     "sitting in dark room, laptop open, monitor glow on face, trading charts visible"),
    ("trade_desk",
     "long black hair, messy bun, tired eyes",
     "baggy hoodie, sweatpants",
     "sitting at desk with multiple monitors, concentrated, dark room, screen light"),
    ("revenge_resolve",
     "long black hair down, simple, no makeup, cold eyes",
     "black hoodie, dark jeans, sneakers",
     "standing on street at night, cold determined expression, city lights, alone"),
]

def upload_ref():
    print("Uploading reference image...")
    with open(REF, "rb") as f:
        r = requests.post(f"{BASE}/upload/image",
                          files={"image": ("shiori_ref.png", f, "image/png")}, timeout=30)
    name = r.json()["name"]
    print(f"  Uploaded: {name}")
    return name

def gen_one(seed, age, fid_weight, base_face, hair, clothes_pose, out_dir, prefix):
    prompt = f"{base_face}, {hair}, {clothes_pose}"
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0],"clip":["1",1],"lora_name":"JapaneseDollLikeness_v15.safetensors","strength_model":L1S,"strength_clip":L1S}},
        "3": {"class_type": "LoraLoader", "inputs": {"model":["2",0],"clip":["2",1],"lora_name":"DetailTweaker.safetensors","strength_model":L2S,"strength_clip":L2S}},
        "4": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["3",0],"preset":"FACEID PLUS V2","lora_strength":0.5,"provider":"CPU"}},
        "5": {"class_type": "LoadImage", "inputs": {"image": REF_NAME}},
        "6": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU","model_name":"buffalo_l"}},
        "7": {"class_type": "IPAdapterFaceID", "inputs": {"model":["4",0],"ipadapter":["4",1],"image":["5",0],"weight":fid_weight,"weight_faceidv2":0.0,"weight_type":"linear","combine_embeds":"concat","start_at":0.0,"end_at":1.0,"embeds_scaling":"V only","insightface":["6",0]}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip":["3",1]}},
        "9": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["3",1]}},
        "10": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "11": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["7",0],"positive":["9",0],"negative":["8",0],"latent_image":["10",0]}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples":["11",0],"vae":["1",2]}},
        "13": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix,"images":["12",0]}},
    }
    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status()
        pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  {prefix} SUBMIT: {e}"); return
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
                                print(f"  {prefix} SAVED ({len(resp.content)//1024}kb)")
                            else:
                                print(f"  {prefix} TOOSMALL ({len(resp.content)}b)")
                    return
                elif st == "error":
                    print(f"  {prefix} ERROR"); return
        except:
            if j == 299: print(f"  {prefix} TIMEOUT")

# Upload reference once
REF_NAME = upload_ref()
if not REF_NAME:
    print("ABORT: upload failed"); exit(1)

total = 0

# ─── 14歳 ───
print(f"\n=== 14歳 中学生 (FaceID 0.8) ===")
BASE14 = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
          "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
          "14 year old japanese girl, middle school student, "
          "slender small build, cute innocent face, still childish features")
total += len(AGE14_VARIANTS)
for i, (tag, hair, clothes_pose, extra) in enumerate(AGE14_VARIANTS, 1):
    seed = random.randint(100000000, 999999999)
    prefix = f"{CHAR}_{tag}_14_yayoi_fid08_s{seed}"
    print(f"[14歳 {i}/{len(AGE14_VARIANTS)}] {tag}")
    gen_one(seed, 14, 0.8, BASE14, hair, f"{clothes_pose}, {extra}", AGE14_DIR, prefix)
    time.sleep(0.3)

# ─── 3歳 ───
print(f"\n=== 3歳 幼児 (FaceID 0.5) ===")
BASE3 = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
         "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "3 year old japanese toddler girl, baby face, chubby round cheeks, "
         "big innocent eyes, small cute nose, "
         "very young child, toddler proportions, short small stature")
total += len(AGE3_VARIANTS)
for i, (tag, hair, clothes_pose, extra) in enumerate(AGE3_VARIANTS, 1):
    seed = random.randint(100000000, 999999999)
    prefix = f"{CHAR}_{tag}_3_yayoi_fid05_s{seed}"
    print(f"[3歳 {i}/{len(AGE3_VARIANTS)}] {tag}")
    gen_one(seed, 3, 0.5, BASE3, hair, f"{clothes_pose}, {extra}", AGE3_DIR, prefix)
    time.sleep(0.3)

# ─── 16歳 ───
print(f"\n=== 16歳 地雷系/トレード (FaceID 0.7) ===")
BASE16 = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
          "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
          "16 year old japanese girl, high school age, "
          "slim build, sharpening facial features, teenage girl")
total += len(AGE16_VARIANTS)
for i, (tag, hair, clothes_pose, extra) in enumerate(AGE16_VARIANTS, 1):
    seed = random.randint(100000000, 999999999)
    prefix = f"{CHAR}_{tag}_16_yayoi_fid07_s{seed}"
    print(f"[16歳 {i}/{len(AGE16_VARIANTS)}] {tag}")
    gen_one(seed, 16, 0.7, BASE16, hair, f"{clothes_pose}, {extra}", AGE16_DIR, prefix)
    time.sleep(0.3)

print(f"\n完了。全{total}枚生成しました。")
