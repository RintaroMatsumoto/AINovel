"""部長55歳: 10バリエーション生成
顔参照なし → IPAdapter不使用、LoRA+プロンプトのみ
"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
W, H, STEPS = 512, 768, 28
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\部長\01_55歳_経理部長"
os.makedirs(OUT, exist_ok=True)

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "feminine, woman, female features, "
       "beard, stubble, facial hair, "
       "young, smooth skin, fresh-faced, "
       "smiling, laughing, happy, cheerful, "
       "casual clothes, t-shirt, hoodie, open collar, no tie")

VARIANTS = [
    ("desk_front", 7.0, "sitting at office desk, front view, reading document, silver wire-rimmed glasses, thin narrow face, calm expression, hands on papers"),
    ("desk_profile", 7.0, "sitting at office desk, profile view, looking at computer monitor, silver wire-rimmed glasses, thin narrow face, concentrated"),
    ("meeting_sofa", 7.0, "sitting on office reception sofa, arm crossed, looking at visitor, silver wire-rimmed glasses, thin narrow face, formal serious"),
    ("office_stand", 7.0, "standing in office near window, hands behind back, looking outside, silver wire-rimmed glasses, thin narrow face, contemplative"),
    ("hallway_walk", 7.0, "walking in office hallway, suit, briefcase, silver wire-rimmed glasses, thin narrow face, mid-stride, professional"),
    ("desk_tired", 7.5, "sitting at desk, leaning back in chair, tired eyes, loosened tie, silver wire-rimmed glasses, thin narrow face, late work"),
    ("meeting_talk", 7.5, "sitting at conference table, gesturing while speaking, silver wire-rimmed glasses, thin narrow face, explaining something"),
    ("office_door", 7.5, "standing by office door, holding file folder, silver wire-rimmed glasses, thin narrow face, about to enter"),
    ("portrait_front", 8.0, "portrait shot, front view, navy suit and tie, silver wire-rimmed glasses, thin narrow face, professional headshot, neutral expression"),
    ("window_profile", 8.0, "side profile, standing by large window, daylight, thoughtful expression, silver wire-rimmed glasses, thin narrow face, arms crossed"),
]

def gen_one(seed, cfg, scene_desc, prefix):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0], "clip":["1",1], "lora_name":"DetailTweaker.safetensors", "strength_model":0.2, "strength_clip":0.2}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip":["2",1]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": scene_desc, "clip":["2",1]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "6": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":cfg,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["2",0], "positive":["4",0], "negative":["3",0], "latent_image":["5",0]}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples":["6",0], "vae":["1",2]}},
        "8": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix, "images":["7",0]}},
    }
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

print("部長55歳: 10バリエーション生成開始...\n")
for i, (tag, cfg, desc) in enumerate(VARIANTS, 1):
    seed = random.randint(100000000, 999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
              f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
              f"55 year old japanese man, division chief, salaryman, "
              f"thin narrow gaunt face, gaunt cheeks, high cheekbones, "
              f"short graying hair, neatly combed, "
              f"silver wire-rimmed glasses, thin metal frame glasses, "
              f"slender lean build, tall and thin, "
              f"navy suit, white shirt, necktie, conservative business attire, "
              f"serious expression, calm, professional, "
              f"experienced, senior manager, authoritative presence, "
              f"{desc}")
    prefix = f"bucho_55_yayoi_cfg{cfg}_s{seed}_{tag}"
    print(f"[{i}/10] {tag} (CFG={cfg})")
    gen_one(seed, cfg, prompt, prefix)
    time.sleep(0.3)
print("\n完了。10枚生成しました。")
