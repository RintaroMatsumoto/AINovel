"""翼0歳: 乳児 10パターン。FaceID不使用。百合子seed(5977)ベース"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA, LS = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘翼\01_0歳_乳児"
os.makedirs(OUT, exist_ok=True)

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "adult, old, toddler, child above 1 year, walking, standing, sitting up unaided")

SCENES = [
    "baby sleeping in crib, peaceful expression, soft blanket, warm room, gentle light, close-up",
    "baby lying on back, looking up with big curious eyes, diaper, soft mat, morning light",
    "baby held in mother's arms, breastfeeding implied, peaceful, warm home, soft focus",
    "baby on tummy, lifting head, trying to crawl, baby onesie, play mat with toys",
    "baby sitting with support, chubby cheeks, drooling, laughing, colorful toys around",
    "baby lying on bed, stretching arms, yawning, just woke up, cute sleepy expression",
    "baby in baby bath, splashing water, happy laughing, bath toys, warm bathroom",
    "baby wrapped in soft towel after bath, being held, warm expression, clean and fresh",
    "baby on play mat, holding rattle toy, looking at it, concentrated baby face",
    "baby close-up portrait, big round eyes, tiny nose, soft baby hair, innocent smile",
]

BASE_PROMPT = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
               "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
               "newborn baby, 0 years old, 3-6 months, japanese baby boy, "
               "tiny delicate features, soft smooth baby skin, chubby round cheeks, "
               "short sparse black baby hair, big round innocent eyes, tiny nose, small mouth, ")

for i, scene in enumerate(SCENES, 1):
    seed = 5977 + i * 7
    prompt = BASE_PROMPT + scene
    prefix = f"tsubasa_0_seed{seed}_{i:02d}"

    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0],"clip":["1",1],"lora_name":"DetailTweaker.safetensors","strength_model":0.2,"strength_clip":0.2}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip":["2",1]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["2",1]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "6": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["2",0],"positive":["4",0],"negative":["3",0],"latent_image":["5",0]}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples":["6",0],"vae":["1",2]}},
        "8": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix,"images":["7",0]}},
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
                            outpath = os.path.join(OUT, img["filename"])
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

print("\n完了。")
