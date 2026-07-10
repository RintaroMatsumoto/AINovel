"""翼20歳v2: ホスト兼格闘家・長髪 各5枚 FaceID"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA, LS = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘翼\06_20歳_タイトルマッチ"
REF = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘翼\02_11歳_小学生\tsubasa_11_yurikos5977_07_00001_.png"
os.makedirs(OUT, exist_ok=True)

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "feminine, woman, female features, effeminate, "
       "makeup, lipstick, eyeshadow, blush, "
       "beard, stubble, facial hair, "
       "colored hair, curly hair, wavy hair, "
       "teenage, childish, boyish, young face, soft features, "
       "thin, skinny, frail, weak")

def gen_one(prompt, prefix, i, total):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0],"clip":["1",1],"lora_name":"DetailTweaker.safetensors","strength_model":0.2,"strength_clip":0.2}},
        "3": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["2",0],"preset":"FACEID PLUS V2","lora_strength":0.5,"provider":"CPU"}},
        "4": {"class_type": "LoadImage", "inputs": {"image": REF_NAME}},
        "5": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU","model_name":"buffalo_l"}},
        "6": {"class_type": "IPAdapterFaceID", "inputs": {"model":["3",0],"ipadapter":["3",1],"image":["4",0],"weight":0.8,"weight_faceidv2":0.0,"weight_type":"linear","combine_embeds":"concat","start_at":0.0,"end_at":1.0,"embeds_scaling":"V only","insightface":["5",0]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip":["2",1]}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["2",1]}},
        "9": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "10": {"class_type": "KSampler", "inputs": {"seed":random.randint(100000000,999999999),"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["6",0],"positive":["8",0],"negative":["7",0],"latent_image":["9",0]}},
        "11": {"class_type": "VAEDecode", "inputs": {"samples":["10",0],"vae":["1",2]}},
        "12": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix,"images":["11",0]}},
    }
    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status()
        pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  [{i}/{total}] SUBMIT: {e}"); return
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
                            if len(resp.content) > 1000:
                                with open(outpath,"wb") as f: f.write(resp.content)
                                print(f"  [{i}/{total}] OK ({len(resp.content)//1024}kb)")
                            else:
                                print(f"  [{i}/{total}] TOOSMALL")
                    break
                elif st == "error":
                    print(f"  [{i}/{total}] ERROR"); break
        except:
            if j == 299: print(f"  [{i}/{total}] TIMEOUT")

print("Uploading...")
with open(REF, "rb") as f:
    r = requests.post(f"{BASE}/upload/image", files={"image": ("tsubasa_ref.png", f, "image/png")}, timeout=30)
REF_NAME = r.json()["name"]
print(f"  OK: {REF_NAME}")

HOST_SCENES = [
    "20 year old japanese man, host club, tall 180cm, muscular build under suit, broad shoulders, long black hair stylishly swept back, hair past ears to neck, sharp piercing eyes, confident arrogant smirk, strong masculine jawline, wearing stylish host suit, designer blazer, open collar white shirt, silver chain, sitting at vip table, legs crossed, leaning back, holding champagne glass, purple neon lights",
    "20 year old japanese man, host, long black hair swept back, sharp eyes, suit, standing at entrance, hands in pockets, full body, looking down with cool smirk, dim luxury interior",
    "20 year old japanese host, close-up portrait, long black hair swept back stylishly, sharp eyes looking slightly away, half smile, expensive suit and silver chain, club background lighting",
    "20 year old japanese host, tall, long black hair, standing at bar leaning on counter, drink in hand, looking over shoulder with piercing gaze, suit jacket, confident",
    "20 year old japanese man, host club, long black hair styled back, walking through floor, suit jacket over shoulder, confident smirk, tall muscular build, luxury interior",
]

FIGHT_SCENES = [
    "20 year old japanese underground fighter, long black hair messy, past ears, sharp intense eyes, muscular athletic build, standing in ring arms raised victory, bloodied but smiling, spotlight, championship belt",
    "20 year old japanese fighter, long messy black hair, cold sharp eyes, muscular build, pre-fight stance, fists up, crouched, ring ropes, arena lights, sweat on body",
    "20 year old fighter, long black hair hanging down, sitting in locker room, leaning forward, hands clasped, focused determined, dark atmosphere, muscular arms visible",
    "close-up portrait, 20 year old fighter, long messy black hair, cold intense stare, small cut on cheek, sweat on skin, sharp eyes, masculine face, fight night lighting",
    "20 year old fighter backstage, long hair tied back loosely, muscular build, hand wraps, dark corridor, focused deadly eyes, alone, waiting for walkout, intense atmosphere",
]

print("\n=== 20歳v2 ホスト (FaceID 0.8) ===")
for i, scene in enumerate(HOST_SCENES, 1):
    prefix = f"tsubasa_20_host_v2_fid08_s{random.randint(100000000,999999999)}_{i:02d}"
    gen_one(scene, prefix, i, 10)
    time.sleep(0.3)

print("\n=== 20歳v2 格闘家 (FaceID 0.8) ===")
for i, scene in enumerate(FIGHT_SCENES, 1):
    prefix = f"tsubasa_20_fight_v2_fid08_s{random.randint(100000000,999999999)}_{i:02d}"
    gen_one(scene, prefix, i+5, 10)
    time.sleep(0.3)

print("\n完了。全10枚生成。")
