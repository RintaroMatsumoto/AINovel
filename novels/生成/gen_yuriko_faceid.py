"""
百合子18歳: IPAdapterFaceID で顔固定生成
seed ランダム × 12バリエーション
"""
import requests, json, time, urllib.request, os, random

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "JapaneseDollLikeness_v15.safetensors", 0.5
LORA2, L2S = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR_NAME = "yuriko"
AGE = "18"
MODEL_NAME = "yayoi_mix"
OUT = rf"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\02_18歳_回想_新入社員"
os.makedirs(OUT, exist_ok=True)

REF_IMG = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\02_18歳_回想_新入社員\yuriko_face_s5977_00001_.png"

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "makeup, frills, lace, ribbon, curly hair, wavy hair, "
       "low ponytail, long ponytail, hair past shoulders, long hair")

BASE_FACE = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
             "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
             "japanese young woman, 18 years old, petite small frame, "
             "plain natural face")

VARIANTS = [
    # (name, hair, clothes_pose)
    ("uniform_bob_front",
     "short black bob haircut, hair ends at jawline",
     "navy blazer with gold buttons, white blouse, knee-length navy skirt, classic japanese office lady uniform, "
     "front view, standing, facing camera, looking at viewer"),
    ("uniform_tied_threeq",
     "short bob hair pulled back, small ponytail at nape, sideswept bangs",
     "navy blazer with gold buttons, white blouse, knee-length navy skirt, classic japanese office lady uniform, "
     "three-quarter view, walking with handbag, looking slightly to the side"),
    ("uniform_bob_threeq",
     "short black bob haircut, hair ends at jawline",
     "navy blazer with gold buttons, white blouse, knee-length navy skirt, classic japanese office lady uniform, "
     "three-quarter view, standing, holding document, looking down slightly"),
    ("cardigan_bob_front",
     "short black bob haircut, hair ends at jawline",
     "warm beige cardigan over cream top, brown knee-length skirt, "
     "front view, sitting on chair, facing camera, hands on lap"),
    ("cardigan_tied_sit",
     "short bob hair pulled back, small ponytail at nape, sideswept bangs",
     "warm beige cardigan over cream top, brown knee-length skirt, "
     "three-quarter view, sitting, looking away thoughtfully"),
    ("knitsweater_bob_profile",
     "short black bob haircut, hair ends at jawline",
     "rust-colored knit sweater, dark brown straight-leg pants, "
     "side view, profile, standing by window, looking outside"),
    ("knitsweater_tied_front",
     "short bob hair pulled back, small ponytail at nape, sideswept bangs",
     "rust-colored knit sweater, dark brown straight-leg pants, "
     "front view, standing, hands in cardigan pocket, facing camera"),
    ("turtleneck_bob_threeq",
     "short black bob haircut, hair ends at jawline",
     "cream turtleneck sweater, olive green A-line knee-length skirt, "
     "three-quarter view, standing, looking up slightly with slight smile"),
    ("turtleneck_tied_desk",
     "short bob hair pulled back, small ponytail at nape, sideswept bangs",
     "cream turtleneck sweater, olive green A-line knee-length skirt, "
     "side view, sitting at desk, looking back over shoulder"),
    ("vest_bob_read",
     "short black bob haircut, hair ends at jawline",
     "light brown knit vest over white blouse, tan knee-length skirt, "
     "profile view, reading document, standing"),
    ("vest_tied_front",
     "short bob hair pulled back, small ponytail at nape, sideswept bangs",
     "light brown knit vest over white blouse, tan knee-length skirt, "
     "front view, carrying tote bag, facing camera, slight smile"),
    ("cardigan_bob_walk",
     "short black bob haircut, hair ends at jawline",
     "warm beige cardigan over cream top, brown knee-length skirt, "
     "three-quarter view, walking down street, looking ahead"),
]

def upload_ref_image():
    """Upload reference face image to ComfyUI"""
    with open(REF_IMG, "rb") as f:
        files = {"image": ("yuriko_ref_18.png", f, "image/png")}
        try:
            r = requests.post(f"{BASE}/upload/image", files=files, timeout=30)
            r.raise_for_status()
            resp = r.json()
            print(f"Upload OK: {resp}")
            return resp["name"]
        except Exception as e:
            print(f"Upload FAILED: {e}")
            return None

def build_workflow(seed, prompt, neg, ref_name, prefix):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model": ["1",0], "clip":["1",1], "lora_name":LORA1, "strength_model":L1S, "strength_clip":L1S}},
        "3": {"class_type": "LoraLoader", "inputs": {"model": ["2",0], "clip":["2",1], "lora_name":LORA2, "strength_model":L2S, "strength_clip":L2S}},
        "4": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["3",0], "preset":"FACEID PLUS V2", "lora_strength":0.5, "provider":"CPU"}},
        "5": {"class_type": "LoadImage", "inputs": {"image": ref_name}},
        "6": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU", "model_name":"buffalo_l"}},
        "7": {"class_type": "IPAdapterFaceID", "inputs": {
            "model":["4",0], "ipadapter":["4",1], "image":["5",0],
            "weight":0.8, "weight_faceidv2":0.0,
            "weight_type":"linear", "combine_embeds":"concat",
            "start_at":0.0, "end_at":1.0, "embeds_scaling":"V only",
            "insightface":["6",0]
        }},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip":["3",1]}},
        "9": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["3",1]}},
        "10": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "11": {"class_type": "KSampler", "inputs": {
            "seed":seed,"steps":STEPS,"cfg":CFG,
            "sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,
            "model":["7",0], "positive":["9",0], "negative":["8",0], "latent_image":["10",0]
        }},
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
                return

# === MAIN ===
print("Step 1/2: Uploading reference image...")
ref_name = upload_ref_image()
if not ref_name:
    print("ABORT: could not upload reference")
    exit(1)

print("Step 2/2: Generating 12 variants...")
for i, (name, hair, clothes_pose) in enumerate(VARIANTS, 1):
    seed = random.randint(1000000000, 9999999999)
    prompt = f"{BASE_FACE}, {hair}, {clothes_pose}"
    prefix = f"{CHAR_NAME}_{AGE}_{MODEL_NAME}_s{seed}_{name}"
    print(f"[{i}/12] s{seed} {name}")
    gen_one(seed, prompt, NEG, ref_name, prefix)
    time.sleep(0.5)
