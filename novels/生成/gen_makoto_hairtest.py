"""誠24歳: 髪型3種×5枚ずつ = 15枚。顔を変えつつ"""
import requests, json, time, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
W, H, STEPS = 512, 768, 28
CFG, SAMPLER, SCHEDULER = 7.0, "dpmpp_2m", "karras"
CHAR, AGE, MODEL = "makoto", "24", "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\00_24歳_参照顔探索"
os.makedirs(OUT, exist_ok=True)

BASE_FACE = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
             "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
             "24 year old japanese man, mid 20s, salaryman, "
             "masculine face, strong jawline, sharp features, no glasses")

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, jewelry, earring, necklace, "
       "beard, stubble, facial hair, "
       "glasses, spectacles, eyewear, "
       "younger than 20, teenager, "
       "feminine, woman, female features, androgynous, ambiguous gender, "
       "soft face, delicate, pretty, girly, effeminate, "
       "pompadour, quiff, slicked back, heavy wax, excessive volume, "
       "sharp sideburns, host style, flashy hair, gel hair, "
       "spiky hair, extreme two block, undercut, "
       "curly hair, wavy hair, colored hair, long hair")

# 3 hairstyles
HAIR_A = ("short natural hairstyle, bangs down, natural side part, "
          "clean but not overstyled, modest office hair, "
          "just showered natural look, soft bangs touching eyebrows")

HAIR_B = ("natural side parted short hair, 70-30 side part, "
          "late 2000s japanese salaryman hairstyle, "
          "neat side part, classic office man hairstyle, "
          "conservative business haircut, clean professional")

HAIR_C = ("soft two-block haircut, short top, "
          "not extreme, natural transition, "
          "minimal undercut, conservative casual")

# 5 scenes x 3 styles = 15
SCENES = [
    ("navy suit, white dress shirt, red tie",
     "standing in office hallway, front view, looking at camera",
     "serious earnest expression, calm",
     "fluorescent light, modern office"),
    ("white shirt, no tie, sleeves rolled",
     "sitting at desk, looking at document",
     "patient slightly tired expression",
     "afternoon office, papers, desk lamp"),
    ("navy suit jacket, white shirt, loosened tie",
     "profile view, walking with briefcase",
     "focused determined look",
     "bright corridor, late 2000s"),
    ("white shirt, vest, no jacket",
     "three-quarter angle, leaning on desk",
     "thoughtful analytical expression",
     "computer monitor, evening light"),
    ("navy suit, red tie",
     "standing by window, looking outside",
     "quiet contemplative expression",
     "window light, city view, afternoon"),
]

HAIR_TAGS = {"A":"natural_short", "B":"sidepart", "C":"soft_twoblock"}

def gen_one(seed, prompt, neg, prefix):
    p=prompt.replace('"','\\"'); n=neg.replace('"','\\"')
    wf={
        "1":{"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":CKPT}},
        "2":{"class_type":"CLIPTextEncode","inputs":{"text":n,"clip":["1",1]}},
        "3":{"class_type":"CLIPTextEncode","inputs":{"text":p,"clip":["1",1]}},
        "4":{"class_type":"EmptyLatentImage","inputs":{"width":W,"height":H,"batch_size":1}},
        "5":{"class_type":"KSampler","inputs":{"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["1",0],"positive":["3",0],"negative":["2",0],"latent_image":["4",0]}},
        "6":{"class_type":"VAEDecode","inputs":{"samples":["5",0],"vae":["1",2]}},
        "7":{"class_type":"SaveImage","inputs":{"filename_prefix":prefix,"images":["6",0]}},
    }
    try:
        r=requests.post(f"{BASE}/prompt",json={"prompt":wf},timeout=30); r.raise_for_status(); pid=r.json()["prompt_id"]
    except Exception as e: print(f"  {prefix} SUBMIT: {e}"); return
    for j in range(300):
        time.sleep(2)
        try:
            h=requests.get(f"{BASE}/history/{pid}",timeout=10).json()
            if pid in h:
                st=h[pid]["status"]["status_str"]
                if st=="success":
                    for nid,node in h[pid]["outputs"].items():
                        for img in node.get("images",[]):
                            p=urllib.parse.urlencode({"filename":img["filename"],"subfolder":img["subfolder"],"type":img["type"]})
                            outpath=os.path.join(OUT,img["filename"])
                            resp=requests.get(f"{BASE}/view?{p}",timeout=60)
                            if len(resp.content)>1000:
                                with open(outpath,"wb") as f: f.write(resp.content)
                                print(f"  {prefix} OK ({len(resp.content)//1024}kb)")
                    return
                elif st=="error": print(f"  {prefix} ERROR"); return
        except:
            if j==299: print(f"  {prefix} TIMEOUT")

print("誠24歳 髪型3種×5シーン = 15枚...")
total = 0
for hair_label, hair_desc in [("A",HAIR_A),("B",HAIR_B),("C",HAIR_C)]:
    hair_tag = HAIR_TAGS[hair_label]
    for si, (clothes, pose, expr, detail) in enumerate(SCENES):
        seed = random.randint(1000000,9999999)
        prompt = f"{BASE_FACE}, {hair_desc}, {clothes}, {pose}, {expr}, {detail}"
        prefix = f"{CHAR}_{AGE}_{MODEL}_s{seed}_{hair_tag}_s{si+1}"
        total += 1
        print(f"[{total}/15] s{seed} {hair_tag}_s{si+1}")
        gen_one(seed, prompt, NEG, prefix)
        time.sleep(0.3)
print("完了。")
