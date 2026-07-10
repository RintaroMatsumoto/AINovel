"""翼14歳少年院: 超短髪・あずき色ジャージのみ 5枚 FaceID"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA, LS = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘翼\04_14歳_少年院"
REF = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘翼\02_11歳_小学生\tsubasa_11_yurikos5977_07_00001_.png"
os.makedirs(OUT, exist_ok=True)

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "feminine, woman, female features, effeminate, "
       "makeup, long hair, colored hair, smiling, laughing, happy, "
       "white shirt under jacket, white collar, undershirt showing, "
       "completely bald, skinhead, shaved head, no hair, "
       "beard, stubble, facial hair")

print("Uploading...")
with open(REF, "rb") as f:
    r = requests.post(f"{BASE}/upload/image", files={"image": ("tsubasa_ref.png", f, "image/png")}, timeout=30)
REF_NAME = r.json()["name"]
print(f"  OK: {REF_NAME}")

SCENES = [
    "front view, standing in detention cell, looking at camera, hard defensive eyes, thin young build, concrete walls, fluorescent light",
    "sitting on edge of prison bed, hands clasped, looking down, closed-off, small cell, cold atmosphere",
    "three-quarter view, standing in detention hallway, rigid posture, fists at sides, angry resentful eyes ahead",
    "close-up portrait, very short buzzed hair, super short crop, visible black hair stubble on scalp, cold empty eyes, neutral",
    "sitting on floor in corner of cell, back against wall, knees up, arms on knees, looking away, dim light, trapped",
]

for i, scene in enumerate(SCENES, 1):
    seed = random.randint(100000000, 999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
              f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
              f"14 year old japanese boy, juvenile detention inmate, "
              f"very short buzzed hair, super short crop haircut, black hair stubble, "
              f"thin young build, "
              f"wearing azuki-red japanese prison tracksuit, azuki-red tracksuit jacket, azuki-red tracksuit pants, "
              f"defensive hardened expression, angry resentful eyes, "
              f"{scene}")
    prefix = f"tsubasa_14_juv_v3_fid075_s{seed}_{i:02d}"

    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0],"clip":["1",1],"lora_name":"DetailTweaker.safetensors","strength_model":0.2,"strength_clip":0.2}},
        "3": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["2",0],"preset":"FACEID PLUS V2","lora_strength":0.5,"provider":"CPU"}},
        "4": {"class_type": "LoadImage", "inputs": {"image": REF_NAME}},
        "5": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU","model_name":"buffalo_l"}},
        "6": {"class_type": "IPAdapterFaceID", "inputs": {"model":["3",0],"ipadapter":["3",1],"image":["4",0],"weight":0.75,"weight_faceidv2":0.0,"weight_type":"linear","combine_embeds":"concat","start_at":0.0,"end_at":1.0,"embeds_scaling":"V only","insightface":["5",0]}},
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
                            outpath = os.path.join(OUT, img["filename"])
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

print("\n完了。")
