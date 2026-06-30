"""
百合子34歳: パラメータ探索（10枚×異なるDollLoRA/FaceID/CFG/Aging）
"""
import requests, json, time, os, random, urllib.parse, glob

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA2, L2S = "DetailTweaker.safetensors", 0.2
W, H, STEPS = 512, 768, 28
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

# 10 variants: (scene, doll_lora, faceid_weight, cfg, aging_tag, hair_extra, clothes_pose)
CONFIGS = [
    #1
    ("sofa_distant", 0.0, 0.6, 8.0, "strong",
     "long hair down, slightly disheveled",
     "plain comfortable home wear, sitting on sofa, gazing out window, "
     "distant unfocused look, evening, alone in living room, soft lamp light"),
    #2
    ("sofa_distant", 0.15, 0.6, 8.0, "strong",
     "long hair down, slightly disheveled",
     "plain comfortable home wear, sitting on sofa, gazing out window, "
     "distant unfocused look, evening, alone in living room, soft lamp light"),
    #3
    ("kitchen_apron", 0.0, 0.4, 8.0, "strong",
     "long hair tied back loosely in low ponytail",
     "simple house dress with apron, in kitchen, preparing dinner, "
     "turning to look aside, warm evening light, tired smile"),
    #4
    ("kitchen_apron", 0.0, 0.5, 8.0, "strong",
     "long hair tied back loosely in low ponytail",
     "simple house dress with apron, in kitchen, preparing dinner, "
     "turning to look aside, warm evening light, tired smile"),
    #5
    ("night_alone", 0.0, 0.6, 7.0, "strong",
     "long hair down, slightly messy",
     "comfortable worn home wear, sitting at kitchen table, "
     "cup of tea in hands, staring into middle distance, "
     "late night, exhausted vulnerable moment"),
    #6
    ("night_alone", 0.0, 0.6, 9.0, "strong",
     "long hair down, slightly messy",
     "comfortable worn home wear, sitting at kitchen table, "
     "cup of tea in hands, staring into middle distance, "
     "late night, exhausted vulnerable moment"),
    #7
    ("mirror_reflection", 0.0, 0.5, 8.0, "moderate",
     "long hair down, mid-back visible",
     "simple undershirt, in bedroom, standing before dresser mirror, "
     "looking at own reflection, examining face, early morning, pensive"),
    #8
    ("mirror_reflection", 0.0, 0.5, 8.0, "strongest",
     "long hair down, mid-back visible",
     "simple undershirt, in bedroom, standing before dresser mirror, "
     "looking at own reflection, examining face, early morning, pensive"),
    #9
    ("station_wait", 0.0, 0.6, 8.0, "moderate",
     "long hair, windblown slightly",
     "beige trench coat, simple scarf, waiting at train station, "
     "hands in pockets, overcast afternoon, standing alone, thoughtful"),
    #10
    ("station_wait", 0.0, 0.6, 8.0, "strongest",
     "long hair, windblown slightly",
     "beige trench coat, simple scarf, waiting at train station, "
     "hands in pockets, overcast afternoon, standing alone, thoughtful"),
]

AGING_PROMPTS = {
    "moderate": {
        "pos": "mature face, tired eyes, natural aging, realistic skin texture, 34 years old mother of two",
        "neg": ""
    },
    "strong": {
        "pos": ("worn exhausted mother of two, visible aging signs on face, tired worn expression, "
                "realistic older woman face, dark circles under eyes, crows feet around eyes, "
                "no makeup, dull natural skin, morning face"),
        "neg": "young, 20s, fresh, firm, smooth elastic skin, perfect skin, glowing skin"
    },
    "strongest": {
        "pos": ("wrinkled forehead, deep eye bags hanging, hollow cheeks, rough dull skin texture, "
                "sagging jawline, clearly middle aged mother, exhausted haunted look, "
                "years of hidden suffering visible on face, gaunt tired face"),
        "neg": ("young, 20s, fresh, firm, smooth, elastic, flawless, beautiful, pretty, "
                "cute, attractive, glamorous, perfect, bouncy, radiant, clear skin, "
                "youthful, energetic, healthy glow, refreshed")
    },
}

BASE_POS = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
            "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
            "japanese woman, 34 years old, married, plain natural face, no makeup, "
            "long straight black hair, hair reaches middle of back")

BASE_NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
            "cartoon, anime, illustration, painting, 3d render, cgi, "
            "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
            "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
            "watermark, signature, text, logo, existing celebrity, real person, "
            "makeup, frills, lace, ribbon, curly hair, wavy hair, "
            "bangs, bob cut, shoulder-length, hair ends at shoulders, "
            "long hair past waist, very long hair")

def upload_ref_image(path):
    with open(path, "rb") as f:
        r = requests.post(f"{BASE}/upload/image", files={"image": (os.path.basename(path), f, "image/png")}, timeout=30)
    if r.status_code == 200:
        name = r.json()["name"]
        print(f"  Upload OK: {name}")
        return name
    print(f"  Upload FAIL: {r.status_code}")
    return None

def build_workflow(seed, prompt, neg, ref_name, prefix, doll_lora, faceid_w, cfg):
    prompt_esc = prompt.replace('"', '\\"')
    neg_esc = neg.replace('"', '\\"')
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name":CKPT}},
    }
    # LoraLoader for DollLikeness (skip if 0)
    n = "1"
    if doll_lora > 0:
        wf["1a"] = {"class_type": "LoraLoader", "inputs": {"model":["1",0], "clip":["1",1],
            "lora_name":"JapaneseDollLikeness_v15.safetensors", "strength_model":doll_lora, "strength_clip":doll_lora}}
        n = "1a"
    if L2S > 0:
        wf["2"] = {"class_type": "LoraLoader", "inputs": {"model":[n,0], "clip":[n,1],
            "lora_name":LORA2, "strength_model":L2S, "strength_clip":L2S}}
        n = "2"
    wf["3"] = {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {
        "model":[n,0], "preset":"FACEID PLUS V2", "lora_strength":0.5, "provider":"CPU"}}
    wf["4"] = {"class_type": "LoadImage", "inputs": {"image": ref_name}}
    wf["5"] = {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU", "model_name":"buffalo_l"}}
    wf["6"] = {"class_type": "IPAdapterFaceID", "inputs": {
        "model":["3",0], "ipadapter":["3",1], "image":["4",0],
        "weight":faceid_w, "weight_faceidv2":0.0, "weight_type":"linear",
        "combine_embeds":"concat", "start_at":0.0, "end_at":1.0,
        "embeds_scaling":"V only", "insightface":["5",0]}}
    wf["7"] = {"class_type": "CLIPTextEncode", "inputs": {"text": neg_esc, "clip":[n,1]}}
    wf["8"] = {"class_type": "CLIPTextEncode", "inputs": {"text": prompt_esc, "clip":[n,1]}}
    wf["9"] = {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}}
    wf["10"] = {"class_type": "KSampler", "inputs": {
        "seed":seed,"steps":STEPS,"cfg":cfg,"sampler_name":SAMPLER,"scheduler":SCHEDULER,
        "denoise":1.0,"model":["6",0],"positive":["8",0],"negative":["7",0],"latent_image":["9",0]}}
    wf["11"] = {"class_type": "VAEDecode", "inputs": {"samples":["10",0], "vae":["1",2]}}
    wf["12"] = {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix, "images":["11",0]}}
    return wf

def gen_one(seed, prompt, neg, ref_name, prefix, doll_lora, faceid_w, cfg):
    wf = build_workflow(seed, prompt, neg, ref_name, prefix, doll_lora, faceid_w, cfg)
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
                            params = urllib.parse.urlencode({"filename":img["filename"],"subfolder":img["subfolder"],"type":img["type"]})
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

# === MAIN ===
print("Uploading reference face...")
ref_name = upload_ref_image(REF_IMG)

print("Generating 10 configs...")
for i, (scene, doll_lora, faceid_w, cfg, aging_tag, hair_d, clothes_pose) in enumerate(CONFIGS, 1):
    seed = random.randint(1000000000, 9999999999)
    ap = AGING_PROMPTS[aging_tag]
    pos = f"{BASE_POS}, {hair_d}, {clothes_pose}, {ap['pos']}"
    neg = BASE_NEG
    if ap['neg']:
        neg += ", " + ap['neg']
    tag = f"d{doll_lora}_f{faceid_w}_cfg{cfg}_{aging_tag}"
    prefix = f"{CHAR_NAME}_{AGE}_{MODEL_NAME}_s{seed}_{scene}_{tag}"
    print(f"[{i}/10] s{seed} {scene} | Doll={doll_lora} FaceID={faceid_w} CFG={cfg} Aging={aging_tag}")
    gen_one(seed, pos, neg, ref_name, prefix, doll_lora, faceid_w, cfg)
    time.sleep(0.5)
