"""
橘栞: 各年齢10枚×3=30枚 一括生成
参照: hoodie_front_00002 (FaceID)
"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "JapaneseDollLikeness_v15.safetensors", 0.5
LORA2, L2S = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR, MODEL = "shiori", "yayoi_mix"

REF = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘栞\01_14歳_中学生\shiori_13_yayoi_mix_s1193774_casual_hoodie_front_00002_.png"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘栞"

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "adult, mature, old, aging, wrinkles, "
       "heavy makeup, dark eyeshadow, lipstick, dyed hair, colored hair, "
       "blonde hair, brown hair, curly hair, wavy hair")

def upload_ref():
    print("Uploading reference...")
    with open(REF, "rb") as f:
        r = requests.post(f"{BASE}/upload/image",
                          files={"image": ("shiori_ref.png", f, "image/png")}, timeout=30)
    name = r.json()["name"]
    print(f"  OK: {name}")
    return name

def gen_one(out_dir, prefix, prompt, fid_weight, seed):
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
                                print(f"  {prefix} OK ({len(resp.content)//1024}kb)")
                            else:
                                print(f"  {prefix} TOOSMALL")
                    return
                elif st == "error":
                    print(f"  {prefix} ERROR"); return
        except:
            if j == 299: print(f"  {prefix} TIMEOUT")

REF_NAME = upload_ref()
if not REF_NAME:
    print("ABORT"); exit(1)

# ─── 14歳: FaceID 0.8 × 10枚 ───
DIR14 = os.path.join(OUT, "01_14歳_中学生")
os.makedirs(DIR14, exist_ok=True)
print("\n=== 14歳 × 10 ===")
BASE14 = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
          "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
          "14 year old japanese girl, middle school student, "
          "long straight black hair, neat bangs, "
          "slender small build, cute innocent face")
SCENES14 = [
    "school uniform, navy blazer, white blouse, gray pleated skirt, front view, standing, school hallway",
    "school uniform, walking with school bag, three-quarter view, school gate, morning light",
    "school uniform, sitting at desk in classroom, writing, concentrated profile",
    "white t-shirt, gray hoodie, home casual, sitting on sofa, relaxed evening",
    "white blouse, gray cardigan, front portrait, smiling, warm expression",
    "school uniform, side view, standing by window, afternoon sunlight",
    "casual clothes, park bench, holding book, reading, afternoon",
    "school uniform, walking home from school, backpack, sunset light",
    "hoodie, sweatpants, sitting on floor, phone in hand, night",
    "white t-shirt, denim skirt, front view, standing, smiling at camera",
]
for i in range(10):
    seed = random.randint(100000000, 999999999)
    p = f"{BASE14}, {SCENES14[i]}"
    tag = f"14_{i+1:02d}"
    prefix = f"{CHAR}_{tag}_14_fid08_s{seed}"
    print(f"[14歳 {i+1}/10]")
    gen_one(DIR14, prefix, p, 0.8, seed)
    time.sleep(0.3)

# ─── 3歳: FaceID 0.5 × 10枚 ───
DIR3 = os.path.join(OUT, "02_3歳_幼児")
os.makedirs(DIR3, exist_ok=True)
print("\n=== 3歳 × 10 ===")
BASE3 = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
         "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
         "3 year old japanese toddler girl, baby face, chubby round cheeks, "
         "big innocent eyes, short straight black hair, baby bangs")
SCENES3 = [
    "holding vintage french doll in arms, looking at it lovingly, indoor, warm light",
    "sitting on floor, doll in lap, curious expression, discovering doll's back",
    "front view, standing, big innocent smile, cute dress, bright daylight",
    "playing in living room, laughing, colorful toys around, happy",
    "sitting at table, eating with small spoon, messy face, cute",
    "wearing cute floral dress, twirling, laughing, garden",
    "hugging doll tightly, looking up, big eyes, adorable",
    "running in park, arms out, wind in hair, happy childhood",
    "sleeping on sofa, doll beside her, peaceful expression",
    "front portrait, hands on cheeks, playful expression, studio light",
]
for i in range(10):
    seed = random.randint(100000000, 999999999)
    p = f"{BASE3}, {SCENES3[i]}"
    tag = f"3_{i+1:02d}"
    prefix = f"{CHAR}_{tag}_3_fid05_s{seed}"
    print(f"[3歳 {i+1}/10]")
    gen_one(DIR3, prefix, p, 0.5, seed)
    time.sleep(0.3)

# ─── 16歳: FaceID 0.7 × 10枚 ───
DIR16 = os.path.join(OUT, "03_16歳_地雷系")
os.makedirs(DIR16, exist_ok=True)
print("\n=== 16歳 × 10 ===")
BASE16 = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
          "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
          "16 year old japanese girl, high school age, "
          "long black hair, slim build, sharpening features")
SCENES16 = [
    "jirai-kei fashion, white fake fur coat, frill blouse, mini skirt, standing on neon street, night",
    "jirai-kei, black oversized sweater, plaid skirt, platform sneakers, front view, street",
    "dark hoodie, sitting in dark room, laptop open, monitor glow on face, trading",
    "black hoodie, dark jeans, standing on street at night, cold determined expression",
    "jirai-kei, side view, standing under neon light, lonely atmosphere, kabukicho",
    "dark room, multiple monitors, concentrated trading face, keyboard in front",
    "jirai-kei, looking back over shoulder, street background, night, cautious eyes",
    "simple black clothes, sitting at desk with laptop, focused, late night trading",
    "jirai-kei, leaning against wall, arms crossed, defensive pose, neon reflection",
    "dark park at night, sitting on bench, looking down, tired lonely expression",
]
for i in range(10):
    seed = random.randint(100000000, 999999999)
    p = f"{BASE16}, {SCENES16[i]}"
    tag = f"16_{i+1:02d}"
    prefix = f"{CHAR}_{tag}_16_fid07_s{seed}"
    print(f"[16歳 {i+1}/10]")
    gen_one(DIR16, prefix, p, 0.7, seed)
    time.sleep(0.3)

print(f"\n完了。全30枚生成 ({chr(10).join([f'{d}: {len(os.listdir(d))-1}枚' for d in [DIR14,DIR3,DIR16]])})")
