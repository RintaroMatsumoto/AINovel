"""翼17歳v2: 大人っぽく・がっしり・180cm 各5枚 FaceID"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA, LS = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
BASE_DIR = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘翼"
REF = BASE_DIR + r"\02_11歳_小学生\tsubasa_11_yurikos5977_07_00001_.png"

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "feminine, woman, female features, effeminate, "
       "makeup, lipstick, eyeshadow, blush, "
       "beard, stubble, facial hair, "
       "long hair, wavy hair, curly hair, colored hair, "
       "teenage boy, adolescent, childish, boyish, young face, soft features, "
       "thin, skinny, frail, weak body")

def gen_batch(subdir, scenes, prompt_base, prefix_tag):
    out_dir = os.path.join(BASE_DIR, subdir)
    os.makedirs(out_dir, exist_ok=True)
    for i, scene in enumerate(scenes, 1):
        seed = random.randint(100000000, 999999999)
        prompt = f"{prompt_base}, {scene}"
        prefix = f"tsubasa_17_{prefix_tag}_v2_fid08_s{seed}_{i:02d}"

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
            "10": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["6",0],"positive":["8",0],"negative":["7",0],"latent_image":["9",0]}},
            "11": {"class_type": "VAEDecode", "inputs": {"samples":["10",0],"vae":["1",2]}},
            "12": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix,"images":["11",0]}},
        }

        try:
            r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
            r.raise_for_status()
            pid = r.json()["prompt_id"]
        except Exception as e:
            print(f"  [{i}/5] SUBMIT: {e}"); continue

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
                                outpath = os.path.join(out_dir, img["filename"])
                                resp = requests.get(url, timeout=60)
                                if len(resp.content) > 1000:
                                    with open(outpath,"wb") as f: f.write(resp.content)
                                    print(f"  [{i}/5] OK ({len(resp.content)//1024}kb)")
                                else:
                                    print(f"  [{i}/5] TOOSMALL")
                        break
                    elif st == "error":
                        print(f"  [{i}/5] ERROR"); break
            except:
                if j == 299: print(f"  [{i}/5] TIMEOUT")
        time.sleep(0.3)

print("Uploading reference...")
with open(REF, "rb") as f:
    r = requests.post(f"{BASE}/upload/image", files={"image": ("tsubasa_ref.png", f, "image/png")}, timeout=30)
REF_NAME = r.json()["name"]
print(f"  OK: {REF_NAME}")

HOST_BASE = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
             "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
             "17 year old young man, mature looking for age, tall 180cm, "
             "muscular athletic build, broad shoulders, developed chest, strong jawline, "
             "short black hair, neatly styled short crop, "
             "handsome masculine face, confident expression, "
             "wearing smart host suit, beige blazer, white shirt, slim pants, silver chain necklace")

HOST_SCENES = [
    "standing in front of mirror in dressing room, adjusting collar, confident smirk, bright vanity lights, tall lean figure",
    "sitting at host club table, leaning back in chair, arm over backrest, relaxed confident pose, dim purple neon",
    "three-quarter view standing in club, hands in pockets, looking slightly down with cool expression, spotlights",
    "close-up portrait, sharp jawline, short neat hair, silver necklace, cool half-lidded eyes, club blur background",
    "standing at club entrance, hands in blazer pockets, full body shot, tall 180cm, looking out at street, night",
]

FIGHT_BASE = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
              "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
              "17 year old young man, mature muscular build, tall 180cm, "
              "broad shoulders, defined chest and arms, athletic physique, "
              "short black hair, messy short crop, "
              "strong masculine face, sharp jaw, intense eyes, "
              "wearing black compression tank top, black fight shorts, hand wraps")

FIGHT_SCENES = [
    "standing in underground ring, arms raised in victory, muscular arms visible, cocky smirk, spotlight, crowd roar",
    "pre-fight stance, fists up guarding face, crouched, intense focused eyes, muscles tensed, ring ropes, sweat gleam",
    "sitting in locker room, leaning forward, wrapping hands, focused determined expression, muscular shoulders and back",
    "close-up portrait, sweat dripping, bruise on cheekbone, intense unwavering eyes, half smile, fight night atmosphere",
    "standing backstage in dark corridor, arms crossed over chest, tall silhouette, looking towards ring light, waiting",
]

print("\n=== 17歳v2 ホスト (FaceID 0.8) ===")
gen_batch("05_17歳_ホスト格闘家", HOST_SCENES, HOST_BASE, "host")

print("\n=== 17歳v2 格闘家 (FaceID 0.8) ===")
gen_batch("05_17歳_ホスト格闘家", FIGHT_SCENES, FIGHT_BASE, "fight")

print("\n完了。全10枚生成。")
