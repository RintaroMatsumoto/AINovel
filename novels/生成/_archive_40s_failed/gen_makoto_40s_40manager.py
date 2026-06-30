"""誠40歳 退職前: 課長風 40枚
白髪交じり・眼鏡・清潔感ある管理職"""
import requests, json, time, urllib.request, os, random

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "DetailTweaker.safetensors", 0.2
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
       "feminine, woman, female features, androgynous, "
       "soft face, delicate, pretty, girly, effeminate, ambiguous gender, "
       "younger than 20, teenager, "
       "curly hair, wavy hair, colored hair, long hair, "
       "pompadour, quiff, slicked back, heavy wax, excessive volume, "
       "sharp sideburns, host style, flashy hair, gel hair, spiky hair, "
       "extreme two block, undercut, "
       "beard, full beard, long stubble, goatee, facial hair, "
       "black suit, funeral, mourning")

BASE_POS = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
            "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
            "japanese man, in his 40s, section manager, kacho, salaryman, "
            "masculine face, strong jawline, sharp features, clean shaven, "
            "short neatly trimmed salt and pepper hair, conservative side part, "
            "gray at temples, silver mixed, natural graying, well-groomed")

# 40 variants — glasses + clean manager, varied angles/settings
VARIANTS = [
    # (tag, fid_w, cfg, glasses, clothes_pose_detail)
    # === 正面・スーツ (6) ===
    ("front_silver", 0.45, 9.5, "(silver thin metal frame glasses:1.2), wire glasses",
     "navy suit, white shirt, dark red tie, front view, standing in office, looking at camera, calm responsible expression"),
    ("front_black", 0.4, 10.0, "(black semi-rimless glasses:1.2), dark frame business glasses",
     "charcoal grey suit, white shirt, navy tie, front view, standing, composed professional expression, slight tiredness"),
    ("front_reading", 0.45, 9.5, "(silver reading glasses:1.2), thin frame, worn low on nose",
     "navy suit, white shirt, burgundy tie, front view, hands holding document, looking up from paper"),
    ("front_navy", 0.5, 9.0, "(silver thin metal glasses:1.1), wire frame",
     "navy suit, white shirt, navy patterned tie, front view, standing, arms at sides, calm experienced look"),
    ("front_stripe", 0.4, 10.0, "(black thin frame glasses:1.1), semi-rimless",
     "grey suit, white shirt, red navy striped tie, front view, standing, serious expression"),
    ("front_warm", 0.45, 9.5, "(silver wire glasses:1.2), thin metal",
     "navy suit, white shirt, maroon tie, front view, slight tired smile, approachable manager expression"),
    # === デスク・オフィス (8) ===
    ("desk_focus", 0.4, 10.0, "(silver frame glasses:1.2), reading glasses on",
     "white shirt, navy vest, no jacket, sitting at desk, looking at financial report, focused tired eyes, pen in hand"),
    ("desk_computer", 0.45, 9.5, "(black rim glasses:1.1), semi-rimless",
     "white shirt, tie loosened, sleeves rolled, sitting at computer, screen glow on face, concentrated expression"),
    ("desk_phone", 0.4, 9.5, "(silver thin glasses:1.2), wire frame",
     "navy suit jacket on, white shirt, sitting at desk, phone to ear, looking at papers, multitasking expression"),
    ("desk_coffee", 0.45, 10.0, "(black frame glasses:1.1), reading glasses",
     "white shirt, no jacket, tie undone, sitting at desk, holding coffee cup, tired morning expression"),
    ("desk_late", 0.4, 10.0, "(silver glasses slightly pushed up:1.1)",
     "white shirt disheveled, tie askew, sleeves rolled, sitting at desk late, exhausted overworked expression, dim light"),
    ("desk_document", 0.5, 9.0, "(silver half rim glasses:1.2)",
     "navy suit, white shirt, standing at desk, leaning over document, pointing at paper, explaining to someone"),
    ("desk_calc", 0.45, 9.5, "(black frame reading glasses:1.1)",
     "white shirt, vest, sleeves rolled, sitting at desk with calculator and papers, analytical focused expression"),
    ("desk_chart", 0.4, 10.0, "(silver wire glasses:1.2)",
     "white shirt, no tie, navy jacket over chair, sitting at desk, looking at stock charts on monitor, intense focus"),
    # === 会議室 (4) ===
    ("meeting_table", 0.45, 9.5, "(silver thin glasses:1.1)",
     "navy suit, white shirt, dark red tie, sitting at conference table, leaning forward, attentive listening, notebook"),
    ("meeting_present", 0.4, 10.0, "(black semi-rimless glasses:1.2)",
     "navy suit, white shirt, burgundy tie, standing at whiteboard, pointer in hand, explaining to team"),
    ("meeting_chair", 0.5, 9.0, "(silver frame glasses:1.1)",
     "grey suit, white shirt, navy tie, sitting at meeting, arms crossed, thoughtful considering expression"),
    ("meeting_side", 0.45, 10.0, "(silver wire glasses:1.2)",
     "navy suit, white shirt, red tie, profile view, sitting at meeting, looking at speaker, tired attentive expression"),
    # === 廊下・移動 (6) ===
    ("hallway_walk", 0.4, 9.5, "(silver thin glasses:1.1)",
     "navy suit, white shirt, dark red tie, walking through corridor, briefcase in hand, mid-stride, determined expression"),
    ("hallway_door", 0.45, 10.0, "(black frame glasses:1.1)",
     "charcoal suit, white shirt, navy tie, about to enter door, hand on handle, pause, thoughtful look"),
    ("hallway_talk", 0.5, 9.0, "(silver glasses:1.1)",
     "navy suit, white shirt, burgundy tie, standing in hallway, talking to colleague off-frame, professional engaged expression"),
    ("hallway_stairs", 0.4, 10.0, "(silver wire glasses:1.2)",
     "navy suit, white shirt, red tie, walking down stairs, looking down at steps, tired end of day"),
    ("hallway_window", 0.45, 9.5, "(silver frame glasses:1.1)",
     "navy suit, white shirt, maroon tie, pausing in hallway by window, looking outside, contemplative tired expression"),
    ("hallway_quick", 0.4, 9.5, "(black thin glasses:1.1)",
     "grey suit, white shirt, navy striped tie, walking briskly through office, carrying folder, busy manager"),
    # === 窓辺 (4) ===
    ("window_contemplate", 0.45, 10.0, "(silver thin glasses:1.2)",
     "navy suit, white shirt, tie loosened, standing by floor window, looking at city, one hand in pocket, tired thoughtful"),
    ("window_coffee", 0.4, 9.5, "(silver frame glasses:1.1)",
     "navy suit jacket, white shirt, no tie, standing by window, holding coffee cup, looking outside, reflective"),
    ("window_profile", 0.5, 9.0, "(silver reading glasses:1.1)",
     "navy suit, white shirt, dark red tie, profile by window, partial reflection, quiet responsible expression"),
    ("window_phone", 0.45, 9.5, "(black frame glasses:1.1)",
     "navy suit, white shirt, maroon tie, standing by window on phone, looking out, serious conversation"),
    # === カフェ・休憩 (4) ===
    ("cafe_read", 0.4, 10.0, "(silver reading glasses:1.2)",
     "white shirt, navy vest, no jacket, tie loose, sitting in cafe, reading newspaper, coffee cup, relaxed tired"),
    ("cafe_window", 0.45, 9.5, "(silver thin glasses:1.1)",
     "navy suit jacket off, white shirt, no tie, sitting at cafe, looking out window, afternoon break, tired eyes"),
    ("cafe_phone", 0.5, 9.0, "(black rim glasses:1.1)",
     "white shirt, casual jacket, sitting at cafe table, checking phone, slight frown, work concerns"),
    ("cafe_street", 0.4, 9.5, "(silver frame glasses:1.2)",
     "navy suit, overcoat, scarf, sitting at outdoor cafe, holding coffee, looking at street, tired but composed"),
    # === 帰宅・通勤 (4) ===
    ("commute_station", 0.45, 10.0, "(silver thin glasses:1.1)",
     "navy suit, overcoat, scarf, standing on train platform, waiting, tired after work expression"),
    ("commute_walk", 0.4, 9.5, "(silver glasses:1.1)",
     "navy suit, coat over arm, loosened tie, walking on evening street, tired commute expression"),
    ("commute_train", 0.45, 9.5, "(black frame glasses:1.1)",
     "navy suit, holding overhead strap, on train, tired eyes, looking aside, crowded commute"),
    ("commute_conveni", 0.5, 9.0, "(silver thin glasses:1.1)",
     "navy suit, no coat, standing in convenience store, buying dinner, exhausted expression, late night"),
    # === 特殊 (4) ===
    ("elevator", 0.4, 10.0, "(silver frame glasses:1.2)",
     "navy suit, white shirt, red tie, in elevator, profile, watching floor numbers, tired morning face"),
    ("kopier", 0.45, 9.5, "(silver reading glasses:1.1)",
     "white shirt, no jacket, standing at copy machine, looking at output, tired late night expression"),
    ("washroom", 0.4, 10.0, "(silver glasses:1.1)",
     "white shirt, loosened tie, in office washroom, looking at mirror, hands on sink, exhausted midday"),
    ("rooftop", 0.5, 9.0, "(silver thin glasses:1.1)",
     "navy suit, no tie, windblown, standing on office rooftop, looking at city skyline, pensive responsible gaze"),
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

print("誠40歳 退職前 課長風 40枚生成開始...")
print(f"出力先: {OUT}")
ref_name = upload_ref()
if not ref_name: print("ABORT"); exit(1)

for i, (tag, fid_w, cfg, glasses, scene) in enumerate(VARIANTS, 1):
    seed = random.randint(1000000000, 9999999999)
    prompt = f"{BASE_POS}, {glasses}, {scene}"
    prefix = f"{CHAR_NAME}_{AGE}_{MODEL_NAME}_fid{int(fid_w*10)}_cfg{int(cfg)}_s{seed}_{tag}"
    print(f"[{i}/40] {tag} fid{int(fid_w*10)} cfg{int(cfg)}")
    gen_one(seed, prompt, NEG, ref_name, prefix, fid_w, cfg)
    time.sleep(0.5)
print("40枚完了。")
