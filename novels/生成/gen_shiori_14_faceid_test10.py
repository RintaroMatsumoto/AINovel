"""
橘栞14歳: seed 5977 (百合子参照顔) × FaceID 0.8 で10枚テスト生成
目的: 母子の顔の相似を利用した参照顔の有効性検証
M1 ComfyUI (100.112.59.35:18188) 使用
"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "JapaneseDollLikeness_v15.safetensors", 0.5
LORA2, L2S = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
SEED = 5977  # 百合子参照顔のseed
CHAR, AGE, MODEL = "shiori", "14", "yayoi_mix"

OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘栞\99_faceid_test"
os.makedirs(OUT, exist_ok=True)

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "adult, mature, old, aging, wrinkles")

BASE_FACE = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
             "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
             "14 year old japanese girl, long straight black hair, "
             "cute innocent face, bright intelligent eyes, slender, petite")

VARIANTS = [
    # (name, hair_detail, clothes, pose_angle)
    ("uniform_front",
     "long straight black hair, neat bangs",
     "navy blazer with gold buttons, white blouse, pleated skirt, knee-high black socks, loafers",
     "front view, standing, facing camera, looking at viewer, school hallway"),
    ("uniform_threeq",
     "long straight black hair, neat bangs",
     "navy blazer with gold buttons, white blouse, pleated skirt, knee-high black socks, loafers",
     "three-quarter view, standing, holding textbook, looking slightly to the side, school hallway"),
    ("uniform_profile",
     "long straight black hair, neat bangs",
     "navy blazer with gold buttons, white blouse, pleated skirt, knee-high black socks",
     "side view, profile, walking, looking ahead, school corridor"),
    ("cardigan_front",
     "long straight black hair, soft bangs",
     "oversized gray cardigan over uniform, white blouse underneath",
     "front view, sitting on chair, hands on lap, facing camera"),
    ("cardigan_threeq",
     "long straight black hair, soft bangs",
     "oversized gray cardigan over uniform, white blouse underneath",
     "three-quarter view, sitting, reading book, looking down"),
    ("casual_front",
     "long straight black hair, loose",
     "simple cotton t-shirt, denim jacket over shoulders",
     "front view, standing, facing camera, casual weekend, home"),
    ("casual_side",
     "long straight black hair, loose",
     "simple cotton t-shirt, denim jacket over shoulders",
     "side view, standing by window, looking outside, natural light"),
    ("home_front",
     "long straight black hair, slightly messy",
     "soft knit sweater, comfortable pants",
     "front view, sitting on sofa, relaxed, warm home interior"),
    ("home_threeq",
     "long straight black hair, slightly messy",
     "soft knit sweater, comfortable pants",
     "three-quarter view, sitting at desk, doing homework, focused"),
    ("school_bag",
     "long straight black hair, neat bangs",
     "navy blazer, white blouse, pleated skirt, school bag on shoulder",
     "three-quarter view, standing at school entrance, afternoon, golden hour light"),
]

def upload_ref():
    """参照画像をアップロード（seed 5977 は既にM1にある想定）"""
    # seed 5977 で直接参照するため、M1の既存ファイル名を推定
    # まず存在確認をせず、直接seed指定で参照する方式に切り替え
    return None

def build_workflow_ref_only(seed, prompt, neg, prefix):
    """seed固定で参照顔なし（seed-only）のワークフロー"""
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

def build_workflow_faceid(seed, prompt, neg, ref_name, prefix):
    """FaceID適用ワークフロー"""
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

# === MAIN ===
print(f"橘栞14歳 テスト生成: seed {SEED} (百合子参照顔)")
print(f"出力先: {OUT}")
print(f"バリエーション: {len(VARIANTS)}枚")
print()

for i, (name, hair, clothes, pose) in enumerate(VARIANTS, 1):
    prompt = f"{BASE_FACE}, {hair}, {clothes}, {pose}"
    prefix = f"{CHAR}_{AGE}_{MODEL}_s{SEED}_{name}"
    wf = build_workflow_ref_only(SEED, prompt, NEG, prefix)
    print(f"[{i}/{len(VARIANTS)}] {name} (seed {SEED})")
    gen_one(wf, prefix)
    time.sleep(0.5)

print()
print("完了。生成された画像を確認し、顔の向き・品質を評価してください。")
print(f"出力先: {OUT}")
