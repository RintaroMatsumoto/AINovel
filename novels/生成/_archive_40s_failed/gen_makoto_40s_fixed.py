"""誠40歳 修正テスト: FaceID 0.2, CFG 12, LoRAなし, 老化強め"""
import requests, json, time, urllib.request, os, random

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
# NO DetailTweaker LoRA — it smooths skin and makes face younger
W, H, STEPS = 512, 768, 28
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR_NAME = "makoto"
AGE = "40"
MODEL_NAME = "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\02_40歳_退職前"
os.makedirs(OUT, exist_ok=True)

REF_IMG = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\01_24歳_社会人\採用\makoto_24_yayoi_mix_s1193774_sidepart_a4_00001_.png"

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, jewelry, earring, necklace, "
       "feminine, woman, androgynous, "
       "soft face, delicate, pretty, girly, effeminate, beautiful, "
       "ambiguous gender, "
       "younger than 30, youthful, teen, boyish, "
       "smooth skin, soft skin, bright skin, clear skin, glowing skin, "
       "fresh face, babyface, ageless, fair skin, "
       "large eyes, big eyes, luminous eyes, sparkly eyes, doe eyes, "
       "small face, delicate bone structure, high cheekbones, "
       "curly hair, wavy hair, colored hair, long hair, "
       "pompadour, quiff, slicked back, heavy wax, excessive volume, "
       "sharp sideburns, host style, flashy hair, gel hair, spiky hair, "
       "extreme two block, undercut, "
       "beard, full beard, long stubble, goatee, facial hair, "
       "black suit, funeral, mourning")

VARIANTS = [
    (0.2, 12.0,
     "short salt and pepper hair, conservative side part, white at temples, graying silver hair, neat business haircut",
     "(silver thin metal frame glasses:1.1)",
     "navy suit, white shirt, dark red tie, front view, standing, looking at camera, calm experienced expression"),
    (0.2, 12.0,
     "short gray black hair, neat side part, silver temples, graying well-groomed hair",
     "(silver frame glasses:1.1)",
     "white shirt, navy vest, no jacket, sitting at desk, reading document, tired focused expression"),
    (0.2, 12.0,
     "short salt and pepper hair, conservative side part, white temples, natural gray streaks",
     "(silver wire glasses:1.1)",
     "navy suit, white shirt, burgundy tie, profile view, walking through hallway, briefcase, determined"),
    (0.2, 12.0,
     "short gray hair, neat side part, silver at temples, graying professional haircut",
     "(silver thin glasses:1.1)",
     "navy suit jacket, white shirt, tie loosened, standing by window, looking outside, tired thoughtful"),
    (0.2, 12.0,
     "short salt pepper gray hair, side part, white streaks, neat manager haircut",
     "(silver reading glasses:1.1)",
     "white shirt, no tie, sleeves rolled, sitting at cafe, reading paper, relaxed tired expression"),
]

def upload_ref():
    with open(REF_IMG, "rb") as f:
        try:
            r = requests.post(f"{BASE}/upload/image", files={"image": ("makoto_ref_24.png", f, "image/png")}, timeout=30)
            r.raise_for_status(); return r.json()["name"]
        except Exception as e: print(f"Upload failed: {e}"); return None

def gen_one(seed, prompt, neg, ref_name, prefix, fid_w, cfg):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        # NO LoraLoader — DetailTweaker makes skin smooth, counterproductive for aging
        "2": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["1",0], "preset":"FACEID PLUS V2", "lora_strength":0.0, "provider":"CPU"}},
        "3": {"class_type": "LoadImage", "inputs": {"image": ref_name}},
        "4": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU", "model_name":"buffalo_l"}},
        "5": {"class_type": "IPAdapterFaceID", "inputs": {
            "model":["2",0], "ipadapter":["2",1], "image":["3",0],
            "weight":fid_w, "weight_faceidv2":0.0,
            "weight_type":"linear", "combine_embeds":"concat",
            "start_at":0.0, "end_at":1.0, "embeds_scaling":"V only",
            "insightface":["4",0]
        }},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip":["1",1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["1",1]}},
        "8": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "9": {"class_type": "KSampler", "inputs": {
            "seed":seed,"steps":STEPS,"cfg":cfg,
            "sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,
            "model":["5",0], "positive":["7",0], "negative":["6",0], "latent_image":["8",0]
        }},
        "10": {"class_type": "VAEDecode", "inputs": {"samples":["9",0], "vae":["1",2]}},
        "11": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix, "images":["10",0]}},
    }
    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status(); pid = r.json()["prompt_id"]
    except Exception as e: print(f"  {prefix} SUBMIT: {e}"); return
    for j in range(120):
        time.sleep(2)
        try:
            h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
            if pid in h and h[pid]["status"]["status_str"] == "success":
                for nid, node in h[pid]["outputs"].items():
                    for img in node.get("images",[]):
                        url = f"{BASE}/view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
                        out = os.path.join(OUT, img["filename"])
                        urllib.request.urlretrieve(url, out)
                        print(f"  {prefix} OK ({os.path.getsize(out)//1024}kb)")
                return
            elif pid in h and h[pid]["status"]["status_str"] == "error":
                print(f"  {prefix} ERROR"); return
        except:
            if j == 119: print(f"  {prefix} TIMEOUT")

print("誠40歳 修正テスト5枚...")
print("変更点: FaceID 0.2, CFG 12, LoRAなし, negative強化")
ref_name = upload_ref()
if not ref_name: print("ABORT"); exit(1)

for i, (fid_w, cfg, hair, glasses, scene) in enumerate(VARIANTS, 1):
    seed = random.randint(1000000000, 9999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
              f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
              f"japanese man, in his 40s, (aged 40:1.2), section manager, kacho, salaryman, "
              f"(tired aging face:1.3), (weary exhausted eyes:1.2), (dark circles under eyes:1.2), "
              f"(rough weathered skin texture:1.3), (wrinkles on forehead and around eyes:1.2), "
              f"(pronounced nasolabial folds:1.1), "
              f"masculine face, strong angular jawline, sharp features, gaunt, hollow cheeks, "
              f"clean shaven, no facial hair, "
              f"{hair}, {glasses}, {scene}")
    prefix = f"{CHAR_NAME}_{AGE}_{MODEL_NAME}_fid{int(fid_w*10)}_cfg{int(cfg)}_s{seed}_fix{i:02d}"
    print(f"[{i}/5] fid{int(fid_w*10)} cfg{int(cfg)}")
    gen_one(seed, prompt, NEG, ref_name, prefix, fid_w, cfg)
    time.sleep(0.5)
print("完了。")
