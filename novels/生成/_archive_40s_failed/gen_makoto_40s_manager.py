"""誠40歳 退職前: 課長風 10枚
調査ベース: 紺スーツ/白シャツ/控えめネクタイ/短髪白髪交じり/シルバーメガネ(任意)
清潔感・髭なし・管理職らしい落ち着き"""
import requests, json, time, urllib.request, os, random

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "DetailTweaker.safetensors", 0.2
W, H, STEPS = 512, 768, 28
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR_NAME = "makoto"
AGE = "40"
MODEL_NAME = "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\02_40歳_退職前\採用"
os.makedirs(OUT, exist_ok=True)

REF_IMG = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\01_24歳_社会人\採用\makoto_24_yayoi_mix_s1193774_sidepart_a4_00001_.png"

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, jewelry, earring, necklace, "
       "feminine, woman, female features, androgynous, "
       "soft face, delicate, pretty, girly, effeminate, ambiguous gender, "
       "younger than 20, teenager, "
       "curly hair, wavy hair, colored hair, long hair, "
       "pompadour, quiff, slicked back, heavy wax, excessive volume, "
       "sharp sideburns, host style, flashy hair, gel hair, spiky hair, "
       "extreme two block, undercut, "
       "beard, full beard, long stubble, goatee, facial hair, "
       "black suit, funeral, mourning, all black")

# 10 variations — clean manager look
VARIANTS = [
    # (tag, fid_w, cfg, aging, glasses, clothes_pose)
    # === メガネあり (5) ===
    ("glasses_front", 0.45, 9.5,
     "short neatly trimmed salt and pepper hair, conservative side part, silver at temples, graying, well-groomed professional manager",
     "(silver thin metal frame glasses:1.2), subtle wire reading glasses, office eyewear",
     "navy suit, white dress shirt, subdued dark red tie, front view, standing in office, looking at camera, calm experienced expression, composed"),
    ("glasses_desk", 0.4, 10.0,
     "short gray black hair, neat side part, white temples, natural gray streaks, clean cut manager hairstyle",
     "(silver semi-rimless glasses:1.2), thin metal frame, professional eyewear",
     "white shirt, navy suit vest, no jacket, sitting at desk, reviewing document, focused tired expression, reading glasses on"),
    ("glasses_window", 0.45, 9.5,
     "short side part, salt and pepper gray hair, silver temples, natural graying, business haircut",
     "(silver frame glasses:1.1), thin wire glasses",
     "navy suit, white shirt, tasteful navy tie with subtle pattern, standing by window, looking outside thoughtfully, tired responsible expression"),
    ("glasses_meeting", 0.4, 10.0,
     "short neatly combed hair, gray at temples, well-groomed conservative hairstyle, manager cut",
     "(black semi-rimless glasses:1.1), subtle business glasses",
     "navy suit, white shirt, maroon tie, sitting at conference table, leaning forward, attentive listening expression"),
    ("glasses_hallway", 0.5, 9.0,
     "short natural gray salt and pepper hair, side part, neatly trimmed, professional",
     "(silver thin glasses:1.1), metal frame",
     "navy suit, white shirt, burgundy tie, walking through office hallway, carrying folder, mid-stride, serious professional expression"),
    # === メガネなし (5) ===
    ("noglasses_portrait", 0.4, 9.5,
     "short salt and pepper haircut, conservative side part, gray temples, well-groomed manager hairstyle, clean professional",
     "",
     "navy suit, white shirt, dark red tie, front view, standing in office, looking at camera, calm responsible expression"),
    ("noglasses_desk", 0.45, 10.0,
     "short gray black hair, neat side part, silver at temples, graying, clean cut manager",
     "",
     "white shirt, sleeves rolled, no jacket, tie loosened, sitting at desk late, looking at computer, tired focused eyes"),
    ("noglasses_phone", 0.4, 9.5,
     "short salt and pepper hair, side part, neatly groomed, gray temples, executive hairstyle",
     "",
     "navy suit jacket, white shirt, navy tie, standing by office window, phone to ear, serious talking expression, concerned"),
    ("noglasses_profile", 0.5, 9.0,
     "short gray black hair, conservative side part, white temples, natural graying, clean shaven",
     "",
     "navy suit, white shirt, dark burgundy tie, profile view, walking with briefcase, determined tired expression"),
    ("noglasses_cafe", 0.45, 9.5,
     "short neatly groomed salt and pepper hair, side part, gray temples, well-groomed",
     "",
     "white shirt, navy vest, no jacket, loosened tie, sitting in cafe, reading newspaper, relaxed but tired expression"),
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

print("誠40歳 課長風 10枚...")
ref_name = upload_ref()
if not ref_name: print("ABORT"); exit(1)

for i, (tag, fid_w, cfg, hair, glasses, scene) in enumerate(VARIANTS, 1):
    seed = random.randint(1000000000, 9999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
              f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
              f"japanese man, in his 40s, section manager, department chief, kacho, "
              f"masculine face, strong jawline, sharp features, clean shaven, "
              f"{hair}, {glasses}, {scene}")
    prefix = f"{CHAR_NAME}_{AGE}_{MODEL_NAME}_fid{int(fid_w*10)}_cfg{int(cfg)}_s{seed}_{tag}"
    print(f"[{i}/10] {tag} fid{int(fid_w*10)} cfg{int(cfg)}")
    gen_one(seed, prompt, NEG, ref_name, prefix, fid_w, cfg)
    time.sleep(0.5)
print("完了。")
