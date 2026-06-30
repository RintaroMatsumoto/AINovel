"""誠24歳: FaceID weight テスト（七三分け確定）
3 weights (0.6/0.7/0.8) × 3 scenes = 9枚
比較用に参照顔のseed情報をprefixに含める"""
import requests, json, time, urllib.request, os, random

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR_NAME = "makoto"
AGE = "24"
MODEL_NAME = "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\01_FaceIDテスト"
os.makedirs(OUT, exist_ok=True)

# Selected reference: s7103016 sidepart_a4
REF_IMG = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\00_24歳_参照顔探索\makoto_24_yayoi_mix_s7103016_sidepart_a4_00001_.png"

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

BASE_FACE = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
             "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
             "24 year old japanese man, mid 20s, salaryman, "
             "masculine face, strong jawline, sharp features, no glasses")
HAIR = ("natural side parted short hair, 70-30 side part, "
        "late 2000s japanese salaryman hairstyle, "
        "neat side part, classic office man haircut, conservative professional")

SCENES = [
    # (name, clothes_pose_detail)
    ("front_office",
     "navy suit, white dress shirt, red tie, "
     "front view, standing in office hallway, looking at camera, "
     "serious calm expression, fluorescent light"),
    ("desk_focus",
     "white dress shirt, sleeves rolled, no tie, "
     "three-quarter angle, sitting at desk, looking at computer monitor, "
     "focused analytical expression, desk with papers, afternoon light"),
    ("profile_street",
     "navy suit, coat over arm, loosened tie, "
     "side view, walking on street, looking up at building, "
     "determined expression, city street, late afternoon"),
]

WEIGHTS = [0.6, 0.7, 0.8]

def upload_ref_image():
    with open(REF_IMG, "rb") as f:
        files = {"image": ("makoto_ref_24.png", f, "image/png")}
        try:
            r = requests.post(f"{BASE}/upload/image", files=files, timeout=30)
            r.raise_for_status()
            resp = r.json()
            print(f"Upload OK: {resp['name']}")
            return resp["name"]
        except Exception as e:
            print(f"Upload FAILED: {e}")
            return None

def gen_one(seed, prompt, neg, ref_name, prefix, weight):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0], "clip":["1",1], "lora_name":LORA1, "strength_model":L1S, "strength_clip":L1S}},
        "3": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["2",0], "preset":"FACEID PLUS V2", "lora_strength":0.5, "provider":"CPU"}},
        "4": {"class_type": "LoadImage", "inputs": {"image": ref_name}},
        "5": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU", "model_name":"buffalo_l"}},
        "6": {"class_type": "IPAdapterFaceID", "inputs": {
            "model":["3",0], "ipadapter":["3",1], "image":["4",0],
            "weight":weight, "weight_faceidv2":0.0,
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
        print(f"  {prefix} SUBMIT: {e}")
        return
    for j in range(120):
        time.sleep(2)
        try:
            h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
            if pid in h:
                st = h[pid]["status"]["status_str"]
                if st == "success":
                    for nid, node in h[pid]["outputs"].items():
                        for img in node.get("images",[]):
                            url = f"{BASE}/view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
                            out = os.path.join(OUT, img["filename"])
                            urllib.request.urlretrieve(url, out)
                            print(f"  {prefix} OK ({os.path.getsize(out)//1024}kb)")
                    return
                elif st == "error":
                    print(f"  {prefix} ERROR")
                    return
        except:
            if j == 119:
                print(f"  {prefix} TIMEOUT")

print("Step 1/2: Uploading reference image...")
ref_name = upload_ref_image()
if not ref_name:
    print("ABORT: upload failed")
    exit(1)

print("Step 2/2: 3 weights × 3 scenes = 9 images...")
total = 0
for w in WEIGHTS:
    int_w = int(w * 10)  # 6, 7, 8
    for name, scene in SCENES:
        seed = random.randint(1000000000, 9999999999)
        prompt = f"{BASE_FACE}, {HAIR}, {scene}"
        prefix = f"{CHAR_NAME}_{AGE}_{MODEL_NAME}_fid{int_w}_s{seed}_{name}"
        total += 1
        print(f"[{total}/9] fid{int_w} s{seed} {name}")
        gen_one(seed, prompt, NEG, ref_name, prefix, w)
        time.sleep(0.5)
print("完了。")
