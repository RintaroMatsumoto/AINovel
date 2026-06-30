"""誠24歳: 参照顔seed探索。FaceID無し、10 seedsで素の顔を確認"""
import requests, json, time, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
W, H, STEPS = 512, 768, 28
CFG, SAMPLER, SCHEDULER = 7.0, "dpmpp_2m", "karras"
CHAR, AGE, MODEL = "makoto", "24", "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\00_24歳_参照顔探索"
os.makedirs(OUT, exist_ok=True)

POS = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
       "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
       "24 year old japanese man, mid 20s, "
       "short neat black hair, young serious face, silver glasses, "
       "white dress shirt, navy suit, dark red tie, "
       "late 2000s japanese salaryman style, "
       "office worker, earnest patient expression, "
       "bright office hallway, natural light, looking at camera")

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, jewelry, earring, necklace, "
       "long hair, curly hair, wavy hair, colored hair, "
       "beard, stubble, facial hair, "
       "younger than 20, teenager, old, elderly, "
       "smile, laughing, happy, joyful")

def gen_one(seed):
    pos = POS.replace('"','\\"')
    neg = NEG.replace('"','\\"')
    wf = {
        "1": {"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":CKPT}},
        "2": {"class_type":"CLIPTextEncode","inputs":{"text":neg,"clip":["1",1]}},
        "3": {"class_type":"CLIPTextEncode","inputs":{"text":pos,"clip":["1",1]}},
        "4": {"class_type":"EmptyLatentImage","inputs":{"width":W,"height":H,"batch_size":1}},
        "5": {"class_type":"KSampler","inputs":{"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["1",0],"positive":["3",0],"negative":["2",0],"latent_image":["4",0]}},
        "6": {"class_type":"VAEDecode","inputs":{"samples":["5",0],"vae":["1",2]}},
        "7": {"class_type":"SaveImage","inputs":{"filename_prefix":f"{CHAR}_{AGE}_{MODEL}_s{seed}_face","images":["6",0]}},
    }
    try:
        r = requests.post(f"{BASE}/prompt",json={"prompt":wf},timeout=30)
        r.raise_for_status(); pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  s{seed} SUBMIT: {e}"); return False
    for j in range(300):
        time.sleep(2)
        try:
            h = requests.get(f"{BASE}/history/{pid}",timeout=10).json()
            if pid in h:
                st = h[pid]["status"]["status_str"]
                if st == "success":
                    for nid,node in h[pid]["outputs"].items():
                        for img in node.get("images",[]):
                            p = urllib.parse.urlencode({"filename":img["filename"],"subfolder":img["subfolder"],"type":img["type"]})
                            url = f"{BASE}/view?{p}"
                            outpath = os.path.join(OUT,img["filename"])
                            resp = requests.get(url,timeout=60)
                            if len(resp.content) > 1000:
                                with open(outpath,"wb") as f: f.write(resp.content)
                                print(f"  s{seed} OK ({len(resp.content)//1024}kb)")
                                return True
                    print(f"  s{seed} no image data"); return False
                elif st == "error": print(f"  s{seed} ERROR"); return False
        except:
            if j == 299: print(f"  s{seed} TIMEOUT"); return False

print("誠24歳 参照顔seed探索 (FaceID無し)...")
seeds = [random.randint(1000000,9999999) for _ in range(12)]
for i, seed in enumerate(seeds, 1):
    print(f"[{i}/12] s{seed}")
    gen_one(seed)
    time.sleep(0.3)
print("完了。確認して、一番良い顔のseedを教えてください。")
