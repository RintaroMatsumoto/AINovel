"""百合子34歳: 劣化追加。Config#3 + Aging extra（strongとstrongestの間）"""
import requests, json, time, os, random, urllib.parse, glob

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA2, L2S = "DetailTweaker.safetensors", 0.2
W, H, STEPS = 512, 768, 28
CFG, SAMPLER, SCHEDULER = 8.0, "dpmpp_2m", "karras"
DOLL_LORA, FACEID_W = 0.0, 0.4
CHAR, AGE, MODEL = "yuriko", "34", "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\01_34歳_現在_主婦"
os.makedirs(OUT, exist_ok=True)

novels_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fm = glob.glob(os.path.join(novels_dir, "novels", "**", "yuriko_face_s5977_00001_.png"), recursive=True)
REF = fm[0] if fm else None
if not REF: print("ERROR: ref not found"); exit(1)

BASE_POS = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
            "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
            "japanese woman, 34 years old, married, mother of two, plain natural face, no makeup, "
            "long straight black hair, hair reaches middle of back")

# extra aging: between strong and strongest
AGING_EXTRA = ("worn exhausted mother of two, visible aging signs on face, "
               "dull tired skin, slightly hollow eyes, gaunt exhausted look, "
               "weathered face with fine lines, dark circles under eyes, "
               "crows feet around eyes, rough natural skin texture, "
               "years of hidden suffering visible on face, no makeup, "
               "realistic mature woman, morning face without sleep")

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, ribbon, curly hair, wavy hair, "
       "bangs, bob cut, shoulder-length, hair ends at shoulders, "
       "long hair past waist, very long hair, "
       "young, 20s, fresh, firm, smooth elastic skin, perfect skin, glowing skin, "
       "beautiful, pretty, cute, attractive, glamorous, flawless, bouncy, radiant, "
       "clear skin, youthful, energetic, healthy glow, refreshed")

VARIANTS = [
    ("livingroom_profile_extra",
     "long hair down, some strands over face",
     "simple comfortable knit sweater, sitting on sofa, "
     "profile view, looking down at hands in lap, "
     "morning light, quiet melancholy"),
    ("dining_side_extra",
     "long hair, side part",
     "plain shirt, at dining table with coffee cup, "
     "side angle 45 degrees, staring at coffee, "
     "midday, still alone"),
    ("veranda_rain_extra",
     "long hair slightly damp",
     "worn cardigan over simple dress, standing under veranda eaves, "
     "looking up at rainy sky, three-quarter angle, "
     "gray daylight, hand touching neck, pensive"),
    ("bedroom_wardrobe_extra",
     "long hair, reaching to touch wardrobe",
     "old worn t-shirt, standing before open wardrobe, "
     "reaching out to touch a jacket sleeve, "
     "back angled toward mirror, looking aside, nostalgic"),
    ("entrance_evening_extra",
     "long hair slightly messy at ends",
     "simple slip-on shoes and home clothes, sitting on entrance step, "
     "tying shoelaces looking up, caught in door light, "
     "evening glow, tired small smile"),
]

def upload_ref(path):
    with open(path,"rb") as f:
        r=requests.post(f"{BASE}/upload/image",files={"image":(os.path.basename(path),f,"image/png")},timeout=30)
    if r.status_code==200: return r.json()["name"]
    print(f"Upload FAIL: {r.status_code}"); return None

def build_wf(seed, prompt, neg, ref_name, prefix):
    p=prompt.replace('"','\\"'); n=neg.replace('"','\\"')
    wf={
        "1":{"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":CKPT}},
        "2":{"class_type":"LoraLoader","inputs":{"model":["1",0],"clip":["1",1],"lora_name":LORA2,"strength_model":L2S,"strength_clip":L2S}},
        "3":{"class_type":"IPAdapterUnifiedLoaderFaceID","inputs":{"model":["2",0],"preset":"FACEID PLUS V2","lora_strength":0.5,"provider":"CPU"}},
        "4":{"class_type":"LoadImage","inputs":{"image":ref_name}},
        "5":{"class_type":"IPAdapterInsightFaceLoader","inputs":{"provider":"CPU","model_name":"buffalo_l"}},
        "6":{"class_type":"IPAdapterFaceID","inputs":{"model":["3",0],"ipadapter":["3",1],"image":["4",0],"weight":FACEID_W,"weight_faceidv2":0.0,"weight_type":"linear","combine_embeds":"concat","start_at":0.0,"end_at":1.0,"embeds_scaling":"V only","insightface":["5",0]}},
        "7":{"class_type":"CLIPTextEncode","inputs":{"text":n,"clip":["2",1]}},
        "8":{"class_type":"CLIPTextEncode","inputs":{"text":p,"clip":["2",1]}},
        "9":{"class_type":"EmptyLatentImage","inputs":{"width":W,"height":H,"batch_size":1}},
        "10":{"class_type":"KSampler","inputs":{"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["6",0],"positive":["8",0],"negative":["7",0],"latent_image":["9",0]}},
        "11":{"class_type":"VAEDecode","inputs":{"samples":["10",0],"vae":["1",2]}},
        "12":{"class_type":"SaveImage","inputs":{"filename_prefix":prefix,"images":["11",0]}},
    }
    return wf

def gen_one(seed, prompt, neg, ref_name, prefix):
    wf=build_wf(seed, prompt, neg, ref_name, prefix)
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
                            url=f"{BASE}/view?{p}"; out=os.path.join(OUT,img["filename"])
                            resp=requests.get(url,timeout=60)
                            with open(out,"wb") as f: f.write(resp.content)
                            print(f"  {prefix} OK ({len(resp.content)//1024}kb)")
                    return
                elif st=="error": print(f"  {prefix} ERROR"); return
        except:
            if j==299: print(f"  {prefix} TIMEOUT")

print("Upload ref...")
ref_name=upload_ref(REF)
if not ref_name: exit(1)

for i,(name,hair_d,clothes_pose) in enumerate(VARIANTS,1):
    seed=random.randint(1000000000,9999999999)
    prompt=f"{BASE_POS}, {hair_d}, {clothes_pose}, {AGING_EXTRA}"
    prefix=f"{CHAR}_{AGE}_{MODEL}_s{seed}_{name}"
    print(f"[{i}/5] s{seed} {name}")
    gen_one(seed,prompt,NEG,ref_name,prefix)
    time.sleep(0.5)
