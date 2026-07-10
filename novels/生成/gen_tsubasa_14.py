"""翼14歳: 里親 + 少年院 各10枚 FaceID"""
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
       "makeup, long hair, colored hair, smiling, laughing, happy, cheerful")

def gen_batch(age_name, out_dir, scenes, fid_weight, base_desc):
    os.makedirs(out_dir, exist_ok=True)
    for i, scene in enumerate(scenes, 1):
        seed = random.randint(100000000, 999999999)
        prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
                  f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
                  f"{base_desc}, {scene}")
        prefix = f"tsubasa_14_{age_name}_fid{fid_weight:.1f}_s{seed}_{i:02d}"

        wf = {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
            "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0],"clip":["1",1],"lora_name":"DetailTweaker.safetensors","strength_model":0.2,"strength_clip":0.2}},
            "3": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["2",0],"preset":"FACEID PLUS V2","lora_strength":0.5,"provider":"CPU"}},
            "4": {"class_type": "LoadImage", "inputs": {"image": REF_NAME}},
            "5": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU","model_name":"buffalo_l"}},
            "6": {"class_type": "IPAdapterFaceID", "inputs": {"model":["3",0],"ipadapter":["3",1],"image":["4",0],"weight":fid_weight,"weight_faceidv2":0.0,"weight_type":"linear","combine_embeds":"concat","start_at":0.0,"end_at":1.0,"embeds_scaling":"V only","insightface":["5",0]}},
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
            print(f"  [{i}/10] SUBMIT: {e}"); continue

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
                                    print(f"  [{i}/10] OK ({len(resp.content)//1024}kb)")
                                else:
                                    print(f"  [{i}/10] TOOSMALL")
                        break
                    elif st == "error":
                        print(f"  [{i}/10] ERROR"); break
            except:
                if j == 299: print(f"  [{i}/10] TIMEOUT")
        time.sleep(0.3)

# Upload reference
print("Uploading reference...")
with open(REF, "rb") as f:
    r = requests.post(f"{BASE}/upload/image", files={"image": ("tsubasa_ref.png", f, "image/png")}, timeout=30)
REF_NAME = r.json()["name"]
print(f"  OK: {REF_NAME}")

# ─── 里親 (FaceID 0.75) ───
DIR_FOSTER = BASE_DIR + r"\03_14歳_里親"
SCENES_FOSTER = [
    "sitting alone in small dark room, scared expression, hugging knees, foster home room, dim light",
    "standing in foster home kitchen, thin fragile build, looking down, sad lonely, plain cheap clothes",
    "sitting on floor in corner, defensive posture, arms around legs, scared eyes, institutional room",
    "in foster home bedroom, small bed, plain room, looking out window, sad expression, evening light",
    "sitting at simple table, no food in front, hollow tired eyes, abused child, quiet despair",
    "standing in dark hallway, thin small figure, looking back over shoulder, frightened, foster home",
    "hiding under blanket on bed, clutching blanket, scared trembling, dark room, alone",
    "sitting on floor, back against wall, knees pulled up, face hidden in arms, crying alone",
    "in foster home living room, standing still, frozen expression, wary eyes, watching surroundings",
    "close-up portrait, thin face, hollow cheeks, tired defeated eyes, abused child, dark background",
]

print("\n=== 14歳 里親 (FaceID 0.75) ===")
gen_batch("foster", DIR_FOSTER, SCENES_FOSTER, 0.75,
          "14 year old japanese boy, thin malnourished build, abused child, "
          "sad tired eyes, fragile, wearing plain cheap clothes, short black hair unkempt")

# ─── 少年院 (FaceID 0.75) ───
DIR_JUV = BASE_DIR + r"\04_14歳_少年院"
SCENES_JUV = [
    "standing in juvenile detention cell, shaved head buzz cut, azuki-red tracksuit, defensive hardened look",
    "sitting on prison bed, buzz cut, empty hardened eyes, closed-off expression, concrete walls",
    "standing in detention hallway, rigid posture, fists clenched, angry suppressed rage, institutional lights",
    "close-up portrait, shaved head, cold dead eyes, no expression, juvenile detention uniform",
    "sitting in corner of cell, knees pulled up, buzz cut, thin but starting to build muscle, alone",
    "walking in detention yard, guarded posture, looking down, prison tracksuit, gray sky",
    "in detention cafeteria, sitting alone at table, not eating, hollow stare, buzzing lights overhead",
    "in detention gym, doing pushups, young thin body building strength, sweat, determined angry face",
    "sitting on cell floor, back against wall, looking up at small window, trapped, quiet fury",
    "face portrait, shaved head, bruise on cheek, defiant eyes, angry teenager, juvenile detention",
]

print("\n=== 14歳 少年院 (FaceID 0.75) ===")
gen_batch("juv", DIR_JUV, SCENES_JUV, 0.75,
          "14 year old japanese boy, juvenile detention inmate, "
          "shaved head buzz cut, thin building muscle, "
          "hardened angry eyes, defensive closed-off posture, "
          "wearing azuki-red prison tracksuit")

print("\n完了。全20枚生成。")
