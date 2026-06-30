"""誠40歳: 加齢パラメータ探索 10枚
FaceID 0.3/0.5/0.7 × CFG 8~10 + aging prompts"""
import requests, json, time, urllib.request, os, random

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "DetailTweaker.safetensors", 0.2
W, H, STEPS = 512, 768, 28
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR_NAME = "makoto"
AGE = "40"
MODEL_NAME = "yayoi_mix"
MODEL = "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\02_40歳_探索"
os.makedirs(OUT, exist_ok=True)

REF_IMG = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\01_24歳_社会人\採用\makoto_24_yayoi_mix_s1193774_sidepart_a4_00001_.png"

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, jewelry, earring, necklace, "
       "glasses, spectacles, eyewear, "
       "feminine, woman, female features, androgynous, "
       "soft face, delicate, pretty, girly, effeminate, ambiguous gender, "
       "younger than 20, teenager, "
       "curly hair, wavy hair, colored hair, long hair, "
       "pompadour, quiff, slicked back, heavy wax, excessive volume, "
       "sharp sideburns, host style, flashy hair, gel hair, spiky hair, "
       "extreme two block, undercut")

BASE_POS = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
            "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
            "japanese man, salaryman, "
            "masculine face, strong jawline, sharp features, "
            "short neatly combed black gray salt and pepper hair, natural side part")

# 10 variations: mix of pre-collapse and post-collapse
VARIANTS = [
    # (tag, fid_w, cfg, aging_positive, clothes_pose)
    # === 現役・崩壊前 (5) ===
    (0.7, 8.0, "mature man in his 40s, early graying at temples, tired but professional eyes, slight crow's feet, ",
     "navy suit, white shirt, dark red tie, standing in office, front view, looking at camera, calm experienced expression"),
    (0.5, 9.0, "man in his late 40s, salt and pepper hair, tired eyes, subtle wrinkles around eyes, aging face, middle aged, ",
     "navy suit jacket, white shirt, loosened tie, sitting at desk, looking at financial reports, focused tired expression"),
    (0.6, 8.5, "40s salaryman, gray streaked hair, slightly weary eyes, experienced face, ",
     "white shirt, sleeves rolled, no tie, three-quarter view, standing by window, thoughtful expression"),
    (0.5, 9.5, "late 40s japanese businessman, graying hair, exhausted eyes, dark circles under eyes, worn face, ",
     "navy suit, red tie, profile view, walking through office corridor, tired determined expression"),
    (0.3, 10.0, "middle aged man, white salt pepper hair, weary sagging eyes, aged skin texture, tired expression, crow's feet, ",
     "white dress shirt, vest, no jacket, sitting in meeting room, leaning back, attentive but tired expression"),
    # === 崩壊後 (5) ===
    (0.5, 9.0, "40s man, completely broken, hollow empty eyes, dark eye circles, gaunt face, unshaven stubble, scruffy beard shadow, disheveled, depressed, heavy eyebags, ",
     "wrinkled white shirt, untucked, first buttons open, messy untidy, sitting in dim room, holding glass of alcohol, destroyed expression"),
    (0.4, 9.5, "broken destroyed man, hollow gaze, vacant eyes, deep dark circles, stubble, unshaven, gaunt hollow cheeks, haggard, aged beyond years, ",
     "rumpled shirt, no tie, disheveled, sitting at home desk, staring at monitors with stock charts, manic desperate look"),
    (0.3, 10.0, "man on the verge, shattered, empty dead eyes, extreme dark circles, gaunt, unkempt beard stubble, disheveled hair, sleep deprived, lifeless expression, ",
     "dirty wrinkled shirt, untucked, in dark room, sitting on floor against wall, head in hands, broken destroyed posture"),
    (0.5, 8.5, "broken middle aged man, unfocused eyes, deep eyebags, stubble shadow, messy salt pepper hair, exhausted desperate expression, ",
     "white shirt stained, tie askew, suit jacket over chair, leaning on desk with both hands, staring down, collapsed expression"),
    (0.4, 9.5, "completely destroyed man, hollow eyes, dead gaze, extreme exhaustion, unshaven days, gaunt sharp features, sunken cheeks, broken spirit, ",
     "worn suit, no tie, disheveled, walking in rain on dark street, head down, slumped posture, aimless wandering"),
]

def upload_ref():
    with open(REF_IMG, "rb") as f:
        try:
            r = requests.post(f"{BASE}/upload/image", files={"image": ("makoto_ref_24.png", f, "image/png")}, timeout=30)
            r.raise_for_status()
            return r.json()["name"]
        except Exception as e:
            print(f"Upload failed: {e}"); return None

def gen_one(seed, prompt, neg, ref_name, prefix, fid_w, cfg):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0], "clip":["1",1], "lora_name":LORA1, "strength_model":L1S, "strength_clip":L1S}},
        "3": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["2",0], "preset":"FACEID PLUS V2", "lora_strength":0.5, "provider":"CPU"}},
        "4": {"class_type": "LoadImage", "inputs": {"image": ref_name}},
        "5": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU", "model_name":"buffalo_l"}},
        "6": {"class_type": "IPAdapterFaceID", "inputs": {
            "model":["3",0], "ipadapter":["3",1], "image":["4",0],
            "weight":fid_w, "weight_faceidv2":0.0,
            "weight_type":"linear", "combine_embeds":"concat",
            "start_at":0.0, "end_at":1.0, "embeds_scaling":"V only",
            "insightface":["5",0]
        }},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip":["2",1]}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["2",1]}},
        "9": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "10": {"class_type": "KSampler", "inputs": {
            "seed":seed,"steps":STEPS,"cfg":cfg,
            "sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,
            "model":["6",0], "positive":["8",0], "negative":["7",0], "latent_image":["9",0]
        }},
        "11": {"class_type": "VAEDecode", "inputs": {"samples":["10",0], "vae":["1",2]}},
        "12": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix, "images":["11",0]}},
    }
    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status(); pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  {prefix} SUBMIT: {e}"); return
    for j in range(120):
        time.sleep(2)
        try:
            h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
            if pid in h:
                if h[pid]["status"]["status_str"] == "success":
                    for nid, node in h[pid]["outputs"].items():
                        for img in node.get("images",[]):
                            url = f"{BASE}/view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
                            out = os.path.join(OUT, img["filename"])
                            urllib.request.urlretrieve(url, out)
                            print(f"  {prefix} OK ({os.path.getsize(out)//1024}kb)")
                    return
                elif h[pid]["status"]["status_str"] == "error":
                    print(f"  {prefix} ERROR"); return
        except:
            if j == 119: print(f"  {prefix} TIMEOUT")

print("Uploading reference (24yo Makoto)...")
ref_name = upload_ref()
if not ref_name: print("ABORT"); exit(1)

print("10 variations (age 40, varying FID/CFG/prompts)...")
for i, (fid_w, cfg, aging, scene) in enumerate(VARIANTS, 1):
    seed = random.randint(1000000000, 9999999999)
    int_fid = int(fid_w * 10)
    prompt = f"{BASE_POS}, {aging}, {scene}"
    prefix = f"{CHAR_NAME}_{AGE}_{MODEL_NAME}_fid{int_fid}_cfg{int(cfg)}_s{seed}_v{i:02d}"
    print(f"[{i}/10] fid{int_fid} cfg{int(cfg)} s{seed}")
    gen_one(seed, prompt, NEG, ref_name, prefix, fid_w, cfg)
    time.sleep(0.5)
print("完了。結果は 02_40歳_探索/ に出力済み")
