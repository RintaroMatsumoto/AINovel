"""誠24歳: メガネなし・男性化、バリエーション20枚"""
import requests, json, time, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
W, H, STEPS = 512, 768, 28
CFG, SAMPLER, SCHEDULER = 7.0, "dpmpp_2m", "karras"
CHAR, AGE, MODEL = "makoto", "24", "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\00_24歳_参照顔探索"
os.makedirs(OUT, exist_ok=True)

BASE_POS = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
            "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
            "24 year old japanese man, mid 20s, salaryman, "
            "masculine face, strong jawline, sharp features, "
            "short neat black hair, young serious face, no glasses")

BASE_NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
            "cartoon, anime, illustration, painting, 3d render, cgi, "
            "nude, exposed, oversaturated, hdr, airbrushed, "
            "mutated hands, extra fingers, deformed, bad anatomy, "
            "watermark, signature, text, logo, existing celebrity, real person, "
            "makeup, frills, lace, jewelry, earring, necklace, "
            "long hair, curly hair, wavy hair, colored hair, "
            "beard, stubble, facial hair, "
            "glasses, spectacles, eyewear, "
            "younger than 20, teenager, "
            "feminine, woman, female features, androgynous, "
            "soft face, delicate, pretty, girly, effeminate, ambiguous gender")

VARIANTS = [
    # (scene, clothes, pose_angle, expression, extra_detail)
    # office suit variants
    ("office_front",
     "navy suit, white dress shirt, dark red tie",
     "standing in office hallway, front view, looking at camera",
     "serious earnest expression",
     "fluorescent light, modern japanese office, late 2000s"),
    ("office_profile",
     "navy suit, white shirt, tie loosened slightly",
     "profile view, walking through office corridor, briefcase in hand",
     "focused determined look",
     "morning, colleagues in background blur"),
    ("desk_training",
     "white shirt, sleeves rolled up, no tie",
     "sitting at desk, leaning forward, pointing at document",
     "patient teaching expression, slight smile",
     "training new employee, papers on desk, afternoon light"),
    ("desk_focus",
     "white dress shirt, navy suit jacket on chair",
     "three-quarter angle, looking at computer monitor",
     "concentrated serious face",
     "office desk, computer screen glow, late afternoon"),
    ("hallway_walk",
     "navy suit, red tie, id badge",
     "walking through bright hallway, mid-stride, natural pose",
     "thoughtful neutral expression",
     "glass windows, sunlight, corporate building"),
    ("meeting",
     "navy suit, white shirt, red tie",
     "sitting at conference table, hands clasped",
     "attentive listening expression",
     "meeting room, notepad, water glass"),
    ("cafe",
     "white shirt, navy vest, no jacket",
     "sitting at cafe table with coffee, looking aside",
     "relaxed slight tiredness",
     "urban cafe, afternoon break, window light"),
    ("street_day",
     "navy suit, coat over arm, loosened tie",
     "standing on street, looking up at building",
     "determined ambitious expression",
     "city street, late afternoon, golden hour"),
    ("elevator",
     "navy suit, red tie",
     "in elevator, profile, watching floor numbers",
     "neutral morning face",
     "elevator interior, mirror reflection, morning commute"),
    ("document",
     "white shirt, no tie, sleeve garters",
     "looking down at document, holding pen",
     "focused analytical expression",
     "desk with financial reports, calculator, desk lamp evening"),
    ("phone_call",
     "shirt and vest, jacket off",
     "standing by window, phone to ear",
     "serious talking expression, slight furrowed brow",
     "office window background, city view, daytime"),
    ("stairs",
     "navy suit, red tie, briefcase",
     "walking down stairs, looking down at steps",
     "tired end of day expression",
     "stairwell, fluorescent light, evening"),
    ("desk_late",
     "disheveled shirt, no tie, first button open",
     "sitting at desk, leaning back, rubbing eyes",
     "exhausted overworked expression",
     "late night office, dim light, computer glow"),
    ("outside_night",
     "navy suit, coat, scarf",
     "standing at station platform, looking at train approaching",
     "tired weary commute face",
     "train station at night, platform lights, winter"),
    ("home_casual",
     "simple white t-shirt, casual pants",
     "sitting on sofa, holding book, profile",
     "relaxed thoughtful expression",
     "living room, evening lamp, bookshelf background"),
    ("home_desk_trade",
     "casual button-up shirt, no tie",
     "three-quarter angle, looking at dual monitors",
     "intense analytical focus",
     "home office, stock charts on screen, late night"),
    ("rooftop",
     "suit jacket, no tie, windblown",
     "standing on office rooftop, looking at city",
     "pensive ambitious gaze",
     "evening skyline, wind in hair, golden hour"),
    ("washroom",
     "white shirt, vest",
     "in washroom, looking at mirror, hands on sink",
     "morning tired face, splashing water",
     "office washroom, mirror reflection, fluorescent"),
    ("entrance",
     "navy suit, overcoat, scarf",
     "at building entrance, adjusting coat, about to enter",
     "determined morning expression",
     "glass door building entrance, winter morning"),
    ("copy_room",
     "white shirt, tie slightly askew",
     "standing by copy machine, looking at output",
     "bored tired expression",
     "copy room, machine glow, late night overtime"),
]

def gen_one(seed, prompt, neg, name):
    p=prompt.replace('"','\\"'); n=neg.replace('"','\\"')
    wf={
        "1":{"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":CKPT}},
        "2":{"class_type":"CLIPTextEncode","inputs":{"text":n,"clip":["1",1]}},
        "3":{"class_type":"CLIPTextEncode","inputs":{"text":p,"clip":["1",1]}},
        "4":{"class_type":"EmptyLatentImage","inputs":{"width":W,"height":H,"batch_size":1}},
        "5":{"class_type":"KSampler","inputs":{"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["1",0],"positive":["3",0],"negative":["2",0],"latent_image":["4",0]}},
        "6":{"class_type":"VAEDecode","inputs":{"samples":["5",0],"vae":["1",2]}},
        "7":{"class_type":"SaveImage","inputs":{"filename_prefix":f"{CHAR}_{AGE}_{MODEL}_s{seed}_{name}","images":["6",0]}},
    }
    try:
        r=requests.post(f"{BASE}/prompt",json={"prompt":wf},timeout=30); r.raise_for_status(); pid=r.json()["prompt_id"]
    except Exception as e: print(f"  {name} SUBMIT: {e}"); return
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
                                print(f"  {name} OK ({len(resp.content)//1024}kb)")
                    return
                elif st=="error": print(f"  {name} ERROR"); return
        except:
            if j==299: print(f"  {name} TIMEOUT")

print("誠24歳 バリエーション20枚（メガネ無し・男性化）...")
for i,(name,clothes,pose,expr,detail) in enumerate(VARIANTS,1):
    seed=random.randint(1000000,9999999)
    prompt=f"{BASE_POS}, {clothes}, {pose}, {expr}, {detail}"
    print(f"[{i}/20] s{seed} {name}")
    gen_one(seed,prompt,BASE_NEG,name)
    time.sleep(0.3)
print("完了。")
