"""誠 選ばれた3つの顔 × 5角度ずつ = 15枚"""
import requests, json, time, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
W, H, STEPS = 512, 768, 28
CFG, SAMPLER, SCHEDULER = 7.0, "dpmpp_2m", "karras"
CHAR, AGE, MODEL = "makoto", "24", "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\00_24歳_参照顔探索"
os.makedirs(OUT, exist_ok=True)

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, jewelry, earring, necklace, "
       "glasses, spectacles, eyewear, "
       "beard, stubble, facial hair, "
       "feminine, woman, female features, androgynous, ambiguous gender, "
       "soft face, delicate, pretty, girly, effeminate, "
       "younger than 20, teenager, "
       "curly hair, wavy hair, colored hair, long hair, "
       "pompadour, quiff, slicked back, heavy wax, excessive volume, "
       "sharp sideburns, host style, flashy hair, gel hair, spiky hair, "
       "extreme two block, undercut")

# 3 face groups — each keeps original hairstyle
GROUPS = [
    {
        "seed_base": 7103016,
        "tag": "sidepart",
        "hair": ("natural side parted short hair, 70-30 side part, "
                 "late 2000s japanese salaryman hairstyle, neat side part, "
                 "classic office man haircut, conservative professional"),
        "scenes": [
            ("navy suit, white dress shirt, red tie",
             "front view, standing at desk, looking at camera",
             "serious calm expression",
             "office, fluorescent light, desk with papers"),
            ("white shirt, navy vest, sleeves rolled",
             "profile view, looking out window, hand in pocket",
             "thoughtful neutral expression",
             "afternoon office, window light, city view"),
            ("navy suit, red tie, id badge",
             "three-quarter angle, walking with briefcase",
             "focused determined look",
             "bright corridor, glass walls"),
            ("white shirt, loosened tie, jacket off",
             "sitting at conference table, leaning back",
             "attentive relaxed expression",
             "meeting room, notepad, water glass"),
            ("navy suit, white shirt, red tie",
             "standing by elevator, waiting, looking aside",
             "tired morning expression",
             "elevator lobby, morning light"),
        ]
    },
    {
        "seed_base": 5233161,
        "tag": "soft_twoblock",
        "hair": ("soft two-block haircut, short top, "
                 "not extreme, natural transition, "
                 "minimal undercut, conservative casual"),
        "scenes": [
            ("navy suit, white dress shirt, dark red tie",
             "front view, standing in office hallway, looking at camera",
             "serious earnest expression",
             "office corridor, fluorescent light"),
            ("white shirt, sleeves rolled, no tie",
             "profile view, sitting at desk, looking at document",
             "patient focused expression",
             "desk with financial reports, afternoon light"),
            ("navy suit jacket, white shirt, tie loosened",
             "three-quarter angle, walking, briefcase in hand",
             "determined expression",
             "bright corridor, glass windows"),
            ("white shirt, navy vest, no jacket",
             "sitting at desk, leaning toward computer",
             "analytical concentrated face",
             "dual monitors, evening, charts on screen"),
            ("navy suit, red tie",
             "by window, looking outside, partial reflection",
             "quiet contemplative expression",
             "window light, city buildings, afternoon"),
        ]
    },
    {
        "seed_base": 6153856,
        "tag": "natural_short",
        "hair": ("short natural hairstyle, bangs down, soft side part, "
                 "clean but not overstyled, modest office hair, "
                 "just showered natural look, unassuming"),
        "scenes": [
            ("navy suit, white dress shirt, red tie",
             "front view, standing in office, looking at camera",
             "calm steady expression",
             "late 2000s japanese office, fluorescent light"),
            ("white shirt, no tie, sleeves rolled up",
             "profile view, looking at papers in hand",
             "patient explaining expression",
             "desk with training documents, afternoon"),
            ("navy suit, overcoat over arm",
             "three-quarter angle, on street looking up",
             "determined ambitious expression",
             "city street, late afternoon"),
            ("white shirt, loosened tie, jacket off",
             "sitting at desk, drinking coffee, looking aside",
             "slightly tired relaxed expression",
             "cafe, afternoon break, window"),
            ("navy suit, red tie",
             "standing at station platform, profile",
             "tired end of day expression",
             "platform, train approaching, winter evening"),
        ]
    }
]

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
        r=requests.post(f"{BASE}/prompt",json={"prompt":wf},timeout=30); r.raise_for_status()
    except Exception as e: print(f"  {prefix} SUBMIT: {e}"); return
    pid=r.json()["prompt_id"]
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

print("3つの顔 × 5角度 = 15枚...")
total=0
for grp in GROUPS:
    sb = grp["seed_base"]
    tag = grp["tag"]
    hair = grp["hair"]
    for si, (clothes, pose, expr, detail) in enumerate(grp["scenes"], 1):
        seed = random.randint(1000000, 9999999)
        prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
                  f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
                  f"24 year old japanese man, mid 20s, salaryman, "
                  f"masculine face, strong jawline, sharp features, no glasses, "
                  f"{hair}, {clothes}, {pose}, {expr}, {detail}")
        prefix = f"{CHAR}_{AGE}_{MODEL}_s{sb}_{tag}_a{si}"
        total+=1
        print(f"[{total}/15] s{sb} {tag}_a{si}")
        gen_one(seed, prompt, NEG, prefix)
        time.sleep(0.3)
print("完了。")
