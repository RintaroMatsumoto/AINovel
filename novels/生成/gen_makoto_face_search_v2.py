"""誠24歳: メガネなし＋男性化版。既存12シード＋追加8シード"""
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
       "24 year old japanese man, mid 20s, salaryman, "
       "masculine face, strong jawline, sharp features, "
       "short neat black hair, young serious face, "
       "white dress shirt, navy suit, dark red tie, "
       "late 2000s japanese salaryman style, "
       "office worker, earnest patient expression, "
       "bright office hallway, natural light")

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, jewelry, earring, necklace, "
       "long hair, curly hair, wavy hair, colored hair, "
       "beard, stubble, facial hair, "
       "younger than 20, teenager, "
       "feminine, woman, female features, androgynous, "
       "soft face, delicate, pretty, girly, effeminate, ambiguous gender")

# Same 12 seeds + 8 new random
old_seeds = [6879505, 7093441, 2700652, 6064157, 9863662, 4131452,
             3192555, 8274715, 5104538, 3909984, 2682667, 9284599]
new_seeds = [random.randint(1000000,9999999) for _ in range(8)]
seeds = old_seeds + new_seeds

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
        print(f"  s{seed} SUBMIT: {e}"); return
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
                            outpath = os.path.join(OUT,img["filename"])
                            resp = requests.get(f"{BASE}/view?{p}",timeout=60)
                            if len(resp.content) > 1000:
                                with open(outpath,"wb") as f: f.write(resp.content)
                                print(f"  s{seed} OK ({len(resp.content)//1024}kb)")
                    return
                elif st == "error": print(f"  s{seed} ERROR"); return
        except:
            if j == 299: print(f"  s{seed} TIMEOUT")

print("誠24歳 メガネなし＋男性化版 20シード...")
for i, seed in enumerate(seeds, 1):
    print(f"[{i}/{len(seeds)}] s{seed}")
    gen_one(seed)
    time.sleep(0.3)
print("完了。確認よろしく。")
