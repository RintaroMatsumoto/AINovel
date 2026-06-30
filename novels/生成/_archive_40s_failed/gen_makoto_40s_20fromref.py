"""誠40歳: 選択された顔＋髪型で20枚"""
import requests, json, time, urllib.request, os, random

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
W, H, STEPS = 512, 768, 28
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR_NAME = "makoto"
AGE = "40"
MODEL_NAME = "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\02_40歳_退職前"
os.makedirs(OUT, exist_ok=True)

# Use the user-selected image as FaceID reference
REF_IMG = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\02_40歳_退職前\makoto_40_yayoi_mix_fid4_cfg9_s6841399557_front_reading_00001_.png"

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
       "black suit, funeral, mourning")

HAIR = ("short neatly trimmed salt and pepper hair, conservative side part, "
        "gray at temples, silver mixed, well-groomed professional")

GLASSES = "(silver thin metal frame glasses:1.2), subtle wire reading glasses"

VARIANTS = [
    # (tag, clothes_pose_detail)
    # 正面スーツ系 (4)
    ("front_navy",
     "navy suit, white shirt, dark red tie, front view, standing, looking at camera, calm expression"),
    ("front_grey",
     "charcoal grey suit, white shirt, navy tie, front view, standing, hands at sides, composed"),
    ("front_vest",
     "navy suit, white shirt, burgundy tie, front view, hands in pockets, slight tired smile"),
    ("front_coat",
     "navy overcoat over suit, red tie visible, front view, standing outdoors, professional"),
    # デスク系 (4)
    ("desk_computer",
     "white shirt, navy vest, no jacket, sitting at desk, looking at monitor, focused"),
    ("desk_docs",
     "white shirt, tie loosened, sleeves rolled, sitting at desk, papers spread, reading"),
    ("desk_late",
     "white shirt disheveled, tie undone, sitting at desk late, exhausted, dim light"),
    ("desk_coffee",
     "white shirt, no tie, jacket off, sitting at desk, holding coffee, tired morning"),
    # 会議室 (2)
    ("meeting_sit",
     "navy suit, white shirt, dark red tie, sitting at conference table, listening"),
    ("meeting_talk",
     "navy suit, white shirt, burgundy tie, standing in meeting, gesturing, explaining"),
    # 廊下・移動 (4)
    ("hallway_walk",
     "navy suit, white shirt, red tie, walking through office, briefcase, mid-stride"),
    ("hallway_door",
     "grey suit, white shirt, navy tie, about to enter door, hand on handle"),
    ("stairs",
     "navy suit, white shirt, burgundy tie, walking down stairs, looking down"),
    ("elevator",
     "navy suit, white shirt, red tie, in elevator, watching floor numbers, profile"),
    # 窓辺 (2)
    ("window_look",
     "navy suit, white shirt, tie loosened, standing by window, looking out, thoughtful"),
    ("window_profile",
     "navy suit jacket, white shirt, no tie, profile by window, coffee cup in hand"),
    # カフェ・休憩 (2)
    ("cafe_read",
     "white shirt, vest, no jacket, sitting at cafe, reading paper, relaxed"),
    ("cafe_outdoor",
     "navy suit, coat over arm, sitting at outdoor cafe, looking at street"),
    # 通勤 (2)
    ("commute_platform",
     "navy suit, overcoat, scarf, standing on train platform, waiting, tired"),
    ("commute_street",
     "navy suit, loosened tie, coat over arm, walking on evening street, commute"),
]

def upload_ref():
    with open(REF_IMG, "rb") as f:
        try:
            r = requests.post(f"{BASE}/upload/image", files={"image": ("makoto_40_ref.png", f, "image/png")}, timeout=30)
            r.raise_for_status(); return r.json()["name"]
        except Exception as e: print(f"Upload failed: {e}"); return None

def gen_one(seed, prompt, neg, ref_name, prefix):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["1",0], "preset":"FACEID PLUS V2", "lora_strength":0.0, "provider":"CPU"}},
        "3": {"class_type": "LoadImage", "inputs": {"image": ref_name}},
        "4": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU", "model_name":"buffalo_l"}},
        "5": {"class_type": "IPAdapterFaceID", "inputs": {
            "model":["2",0], "ipadapter":["2",1], "image":["3",0],
            "weight":0.4, "weight_faceidv2":0.0,
            "weight_type":"linear", "combine_embeds":"concat",
            "start_at":0.0, "end_at":1.0, "embeds_scaling":"V only",
            "insightface":["4",0]
        }},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip":["1",1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["1",1]}},
        "8": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "9": {"class_type": "KSampler", "inputs": {
            "seed":seed,"steps":STEPS,"cfg":9.5,
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

print("誠40歳 選択顔ベース20枚...")
print(f"参照顔: front_reading (40yo本人)")
ref_name = upload_ref()
if not ref_name: print("ABORT"); exit(1)

for i, (tag, scene) in enumerate(VARIANTS, 1):
    seed = random.randint(1000000000, 9999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
              f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
              f"japanese man, in his 40s, section manager, kacho, salaryman, "
              f"masculine face, strong jawline, sharp features, clean shaven, "
              f"{HAIR}, {GLASSES}, {scene}")
    prefix = f"{CHAR_NAME}_{AGE}_{MODEL_NAME}_fid4_cfg9_s{seed}_{tag}"
    print(f"[{i}/20] {tag}")
    gen_one(seed, prompt, NEG, ref_name, prefix)
    time.sleep(0.5)
print("20枚完了。")
