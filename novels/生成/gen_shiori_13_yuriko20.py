"""
橘栞13歳: seed 5977 (百合子参照顔) × 20枚追加生成
服装・髪型・角度をさらにバリエーション
M1 ComfyUI (100.112.59.35:18188) 使用
"""
import requests, json, time, urllib.request, os, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "JapaneseDollLikeness_v15.safetensors", 0.5
LORA2, L2S = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
SEED = 5977
CHAR, AGE, MODEL = "shiori", "13", "yayoi_mix"

OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘栞\02_13歳_中学生_百合子seed"
os.makedirs(OUT, exist_ok=True)

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "adult, mature, old, aging, wrinkles, "
       "heavy makeup, dark eyeshadow, lipstick, "
       "dyed hair, colored hair, blonde hair, brown hair")

BASE_FACE = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
             "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
             "13 year old japanese girl, second year middle school student, "
             "round childish face, baby fat still visible, "
             "small thin build, still growing, ")

VARIANTS = [
    # 制服系（髪型・角度違い）
    ("school_straight_front",
     "long straight black hair, neat bangs, hair behind ears",
     "navy blazer, white blouse, gray pleated skirt, navy ribbon",
     "front view, standing, facing camera, school gate, morning"),
    ("school_bob_front",
     "short black bob haircut, neat straight bangs, chin length",
     "navy blazer, white blouse, gray pleated skirt, navy ribbon",
     "front view, standing, facing camera, school entrance"),
    ("school_pony_front",
     "long straight black hair tied in low ponytail, neat bangs",
     "navy blazer, white blouse, gray pleated skirt, navy ribbon",
     "front view, standing, facing camera, classroom"),
    ("school_straight_threeq",
     "long straight black hair, neat bangs",
     "navy blazer, white blouse, gray pleated skirt, navy ribbon, school bag",
     "three-quarter view, walking, looking ahead, school corridor"),
    ("school_bob_threeq",
     "short black bob haircut, neat bangs",
     "navy blazer, white blouse, gray pleated skirt",
     "three-quarter view, sitting at desk, writing, classroom"),
    ("school_straight_profile",
     "long straight black hair, neat bangs",
     "navy blazer, white blouse, gray pleated skirt",
     "side view, profile, standing by window, afternoon light"),
    ("school_sportswear",
     "long straight black hair, tied high ponytail",
     "white gym shirt, navy gym shorts, white socks, sneakers",
     "front view, standing, holding ball, school gym"),
    ("school_swimsuit",
     "long straight black hair, wet, tied back",
     "school swimsuit, white with blue trim, holding towel",
     "front view, standing, poolside, summer, still growing"),
    # 私服系（髪型・服装違い）
    ("casual_denim_jacket",
     "long straight black hair, loose, messy bangs",
     "denim jacket, white t-shirt, denim shorts",
     "front view, standing, casual, park, afternoon"),
    ("casual_hoodie_down",
     "long straight black hair, loose, no styling",
     "black oversized hoodie, gray sweatpants",
     "front view, standing, hands in pocket, sidewalk, casual"),
    ("casual_cardigan_hair",
     "shoulder length black hair, loose, soft waves",
     "beige cardigan, white blouse, brown skirt",
     "front view, sitting at cafe, coffee in front"),
    ("casual_tshirt_bun",
     "long straight black hair, messy bun on top",
     "plain white t-shirt, denim overalls",
     "front view, standing, park bench, weekend"),
    ("casual_knit_twin",
     "long straight black hair, low twin tails, small black rubber",
     "cream knit sweater, plaid skirt",
     "front view, standing, bookshelf background"),
    ("casual_sporty",
     "long straight black hair, ponytail",
     "track jacket, black leggings, sneakers",
     "front view, standing, running track, sporty"),
    # 雑貨・シーン違い
    ("scene_library",
     "long straight black hair, neat bangs, reading glasses",
     "cardigan, blouse, plaid skirt",
     "sitting at library desk, reading book, focused, warm light"),
    ("scene_cafe",
     "long straight black hair, soft bangs",
     "casual knit top, comfortable pants",
     "sitting at cafe table, juice, looking at phone, relaxed"),
    ("scene_bookstore",
     "long straight black hair, loose",
     "simple t-shirt, jeans, canvas bag",
     "standing at bookstore, looking at books, profile"),
    ("scene_park_bench",
     "long straight black hair, tucked behind ear",
     "striped long sleeve t-shirt, denim skirt",
     "sitting on park bench, legs crossed, afternoon, relaxed"),
    ("scene_stairwell",
     "long straight black hair, neat bangs",
     "school uniform, navy blazer, skirt",
     "sitting on stairwell, knees up, looking down, quiet, afternoon light"),
]

def build_workflow(seed, prompt, neg, prefix):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model": ["1",0], "clip":["1",1], "lora_name":LORA1, "strength_model":L1S, "strength_clip":L1S}},
        "3": {"class_type": "LoraLoader", "inputs": {"model": ["2",0], "clip":["2",1], "lora_name":LORA2, "strength_model":L2S, "strength_clip":L2S}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip":["3",1]}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["3",1]}},
        "6": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "7": {"class_type": "KSampler", "inputs": {
            "seed":seed,"steps":STEPS,"cfg":CFG,
            "sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,
            "model":["3",0], "positive":["5",0], "negative":["4",0], "latent_image":["6",0]
        }},
        "8": {"class_type": "VAEDecode", "inputs": {"samples":["7",0], "vae":["1",2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix, "images":["8",0]}},
    }

def gen_one(wf, prefix):
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
                            params = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img["subfolder"], "type": img["type"]})
                            url = f"{BASE}/view?{params}"
                            outpath = os.path.join(OUT, img["filename"])
                            resp = requests.get(url, timeout=60)
                            if len(resp.content) > 1000:
                                with open(outpath, "wb") as f: f.write(resp.content)
                                print(f"  {prefix} OK ({len(resp.content)//1024}kb)")
                            else:
                                print(f"  {prefix} EMPTY ({len(resp.content)}b)")
                    return
                elif st == "error":
                    print(f"  {prefix} ERROR"); return
        except:
            if j == 299: print(f"  {prefix} TIMEOUT")

print(f"百合子seed (5977) 追加生成: 20枚")
print(f"出力先: {OUT}")
print()

for i, (name, hair, clothes, pose) in enumerate(VARIANTS, 1):
    prompt = f"{BASE_FACE} {hair}, {clothes}, {pose}"
    prefix = f"{CHAR}_{AGE}_{MODEL}_s{SEED}_{name}"
    print(f"[{i}/{len(VARIANTS)}] {name}")
    gen_one(build_workflow(SEED, prompt, NEG, prefix), prefix)
    time.sleep(0.5)

print()
print("完了。")
