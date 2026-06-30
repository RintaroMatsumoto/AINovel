"""
橘百合子18歳: seed 5977固定 × 制服/私服 × 2髪型 × 3角度 = 12枚
"""
import requests, json, time, urllib.request, os

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "JapaneseDollLikeness_v15.safetensors", 0.5
LORA2, L2S = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\02_18歳_回想_新入社員"
os.makedirs(OUT, exist_ok=True)
SEED = 5977

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "makeup, frills, lace, ribbon, long hair, hair past ears, curly hair, wavy hair, "
       "low ponytail, long ponytail")

BASE_FACE = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
             "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
             "18 year old japanese young woman, petite small frame, "
             "plain natural face, no makeup, t_yuriko_f")

ANGLES = [
    ("front", "front view, facing camera, looking at viewer"),
    ("threeq", "three-quarter view, looking slightly to the side"),
    ("profile", "side view, profile, looking away"),
]

HAIR = [
    ("bob", "short black bob haircut, hair ends at jawline"),
    ("tied", "short bob hair pulled back, tied in small ponytail at nape, tiny tail"),
]

CLOTHES = [
    ("uniform", "navy blazer with gold buttons, white blouse, knee-length navy skirt, classic japanese office lady uniform, professional"),
    ("casual", "warm beige cardigan over cream top, brown knee-length cotton skirt, modest office casual"),
]

def build_prompt(angle_desc, hair_desc, clothes_desc):
    return f"{BASE_FACE}, {hair_desc}, {clothes_desc}, {angle_desc}"

def gen_one(seed, prompt, neg, prefix):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0],"clip":["1",1],"lora_name":LORA1,"strength_model":L1S,"strength_clip":L1S}},
        "9": {"class_type": "LoraLoader", "inputs": {"model":["2",0],"clip":["2",1],"lora_name":LORA2,"strength_model":L2S,"strength_clip":L2S}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["9",1]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip":["9",1]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "6": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["9",0],"positive":["3",0],"negative":["4",0],"latent_image":["5",0]}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples":["6",0],"vae":["1",2]}},
        "8": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix,"images":["7",0]}},
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
                return

total = 0
for clothes_key, clothes_desc in CLOTHES:
    for hair_key, hair_desc in HAIR:
        for angle_key, angle_desc in ANGLES:
            total += 1
            prefix = f"yuriko_s{SEED}_{clothes_key}_{hair_key}_{angle_key}"
            prompt = build_prompt(angle_desc, hair_desc, clothes_desc)
            print(f"[{total}/12] {prefix}")
            gen_one(SEED, prompt, NEG, prefix)
            time.sleep(0.3)
