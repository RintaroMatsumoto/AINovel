"""部長残り4枚: majicMIX + FaceID"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "majicMIX.safetensors"
W, H, STEPS, CFG = 512, 768, 30, 8.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\部長\01_55歳_経理部長"
REF = OUT + r"\bucho_majic_v2_cfg8.0_s889003312_01_00001_.png"
os.makedirs(OUT, exist_ok=True)

NEG = ("(worst quality:1.4), (low quality:1.4), (normal quality:1.2), "
       "EasyNegative, badhandv4, "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, plastic skin, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, "
       "woman, girl, female, feminine, women, girls, "
       "breasts, curves, makeup, lipstick, eyelashes, "
       "jewelry, earring, necklace, "
       "young, smooth skin, radiant, fresh-faced, "
       "smiling, laughing, happy, cheerful")

SCENES = [
    ("window", "standing by office window, hands behind back, looking outside thoughtfully, profile view, natural daylight coming through window, navy suit, thinking expression"),
    ("hallway", "walking in office hallway, carrying briefcase, mid-stride, professional focused expression, three-quarter view, office corridor lighting, navy suit"),
    ("meeting", "sitting at meeting table, hands clasped on table, listening expression, conference room background, serious professional atmosphere, navy suit, red tie"),
    ("reception", "standing in office reception area, arms crossed, looking at visitor with calm authority, front view, navy suit, office lobby background"),
]

print("Uploading reference...")
with open(REF, "rb") as f:
    r = requests.post(f"{BASE}/upload/image", files={"image": ("bucho_ref.png", f, "image/png")}, timeout=30)
REF_NAME = r.json()["name"]
print(f"  OK: {REF_NAME}")

for tag, scene in SCENES:
    seed = random.randint(100000000, 999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
              f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
              f"(male:1.3), (masculine:1.2), 1boy, "
              f"55 year old japanese salaryman, division chief, "
              f"thin narrow gaunt face, deep wrinkles, sunken cheeks, high cheekbones, "
              f"short graying hair, salt and pepper hair, receding hairline, "
              f"silver wire-rimmed glasses, tired experienced eyes, "
              f"slender lean build, "
              f"{scene}")
    prefix = f"bucho_faceid_cfg{CFG}_s{seed}_{tag}"

    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "CLIPSetLastLayer", "inputs": {"clip":["1",1], "stop_at_clip_layer":-2}},
        "3": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["1",0],"preset":"FACEID PLUS V2","lora_strength":0.5,"provider":"CPU"}},
        "4": {"class_type": "LoadImage", "inputs": {"image": REF_NAME}},
        "5": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU","model_name":"buffalo_l"}},
        "6": {"class_type": "IPAdapterFaceID", "inputs": {"model":["3",0],"ipadapter":["3",1],"image":["4",0],"weight":0.8,"weight_faceidv2":0.0,"weight_type":"linear","combine_embeds":"concat","start_at":0.0,"end_at":1.0,"embeds_scaling":"V only","insightface":["5",0]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip":["2",0]}},
        "8": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["2",0]}},
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
        print(f"  [{tag}] SUBMIT: {e}"); continue

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
                                print(f"  [{tag}] OK ({len(resp.content)//1024}kb)")
                            else:
                                print(f"  [{tag}] TOOSMALL")
                    break
                elif st == "error":
                    print(f"  [{tag}] ERROR"); break
        except:
            if j == 299: print(f"  [{tag}] TIMEOUT")
    time.sleep(0.3)

print("\n完了。")
