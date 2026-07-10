"""部長: majicMIX v2 - 性別修正・clip_skip2・DPM++"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "majicMIX.safetensors"
W, H, STEPS, CFG = 512, 768, 30, 8.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\部長\01_55歳_経理部長"
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
       "smiling, laughing, happy, cheerful, ")
# Note: no DetailTweaker - majicMIX doesn't need it

SCENES = [
    "1boy, 55 year old japanese salaryman, division chief, thin gaunt narrow face, deep wrinkles, sunken cheeks, high cheekbones, short graying hair, salt and pepper hair, receding hairline, silver wire-rimmed glasses, tired experienced eyes, dark circles under eyes, slender lean build, navy suit, white shirt, necktie, sitting at office desk, reading document, serious calm professional expression, front view, looking at camera",
    "1boy, 55 year old japanese manager, thin narrow gaunt face, deep wrinkles on forehead and around eyes, graying temples, aging weathered skin, silver wire-rimmed glasses, stern experienced expression, short neatly combed gray hair, standing by office window, hands behind back, looking outside, profile view, navy suit, conservative tie, natural daylight",
    "1boy, 55 year old japanese salaryman, close-up portrait, thin face, deep facial wrinkles, aging skin texture, silver wire-rimmed glasses, tired eyes, graying short hair, receding hairline, serious expression, office background bokeh, professional headshot, looking at camera",
    "1boy, 55 year old japanese division chief, thin narrow face, wrinkles, silver rimmed glasses, gray hair, walking in office hallway, carrying briefcase, mid-stride, professional focused expression, navy suit, office corridor lighting, three-quarter view",
    "1boy, 55 year old japanese businessman, gaunt thin face, aged skin, heavy eyebags, silver wire-rimmed glasses, short salt and pepper hair, sitting at meeting table, hands clasped on table, listening expression, navy suit, white shirt, red tie, conference room, serious atmosphere",
]

print("Testing majicMIX v2 with clip_skip2 and DPM++...")
for i, scene in enumerate(SCENES, 1):
    seed = random.randint(100000000, 999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
              f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
              f"(male:1.3), (masculine:1.2), old man senior citizen, "
              f"{scene}")
    prefix = f"bucho_majic_v2_cfg{CFG}_s{seed}_{i:02d}"

    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "CLIPSetLastLayer", "inputs": {"clip":["1",1], "stop_at_clip_layer":-2}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip":["2",0]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["2",0]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "6": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["1",0],"positive":["4",0],"negative":["3",0],"latent_image":["5",0]}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples":["6",0],"vae":["1",2]}},
        "8": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix,"images":["7",0]}},
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
