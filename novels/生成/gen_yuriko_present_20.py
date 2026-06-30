"""百合子34歳: 20バリエーション探索。プロンプト手法×パラメータを系統的に振る"""
import requests, json, time, os, random, urllib.parse, glob

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
W, H, STEPS = 512, 768, 28
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CHAR, AGE, MODEL = "yuriko", "34", "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\01_34歳_現在_主婦"
os.makedirs(OUT, exist_ok=True)

novels_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fm = glob.glob(os.path.join(novels_dir, "novels", "**", "yuriko_face_s5977_00001_.png"), recursive=True)
REF = fm[0]; print(f"Ref: {REF}")

# === PROMPT APPROACHES ===
P = {}
P["A"] = {
    "pos_prefix": "(masterpiece, best quality:1.2), 8k, RAW photo, "
                  "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
                  "(34-years-old:1.3), mature woman, mother of two, "
                  "long straight black hair, hair reaches middle of back, "
                  "plain natural face, no makeup",
    "pos_aging": "tired heavy-lidded eyes, exhausted distant gaze, "
                 "subtle dark circles under eyes, weary expression, "
                 "quiet resignation in eyes, subtle eye bags",
    "neg_extra": "young, fresh, energetic, bright-eyed, lively, well-rested, "
                 "20s, teen, baby face, innocent, naive, carefree, "
                 "flawless skin, glowing skin, dewy skin, radiant, "
                 "youthful, healthy glow, fresh-faced, clear skin"
}
P["B"] = {
    "pos_prefix": "(masterpiece, best quality:1.2), 8k, RAW photo, "
                  "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
                  "34-years-old, mature woman, thirties, "
                  "long straight black hair, mid-back length hair, "
                  "plain natural face, no makeup",
    "pos_aging": "mother of two, experienced tired gaze, "
                 "distant thoughtful expression, quiet weariness, "
                 "natural aging around eyes, subdued expression",
    "neg_extra": "young, teen, adolescent, childish, "
                 "cute, kawaii, innocent, "
                 "glowing skin, radiant, fresh-faced"
}
P["C"] = {
    "pos_prefix": "(masterpiece, best quality:1.2), 8k, RAW photo, "
                  "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
                  "japanese woman, 34 years old, married, mother of two, "
                  "long straight black hair, hair reaches middle of back, "
                  "plain natural face, no makeup",
    "pos_aging": "worn exhausted mother, visible aging signs on face, "
                 "tired worn expression, realistic older woman face, "
                 "dark circles under eyes, crows feet around eyes, "
                 "no makeup, dull natural skin, morning face",
    "neg_extra": "young, 20s, fresh, firm, smooth elastic skin, perfect skin, glowing skin"
}

SCENES = [
    ("sofa_profile", "long hair down, some strands over face",
     "simple knit sweater, sitting on sofa, profile view, looking down at hands in lap, morning light, quiet"),
    ("kitchen_apron", "long hair tied back loosely",
     "simple house dress with apron, in kitchen, preparing dinner, turning to look aside, warm evening light, tired"),
    ("dining_side", "long hair, side part",
     "plain shirt, at dining table with coffee cup, side angle 45 degrees, staring at coffee, midday, alone"),
    ("mirror_reflection", "long hair down, mid-back visible",
     "simple undershirt, standing before dresser mirror, looking at own reflection, early morning, pensive"),
    ("night_alone", "long hair down, slightly messy",
     "worn home wear, sitting at kitchen table with tea, staring into middle distance, late night, exhausted"),
    ("entrance_evening", "long hair slightly messy at ends",
     "slip-on shoes, home clothes, sitting on entrance step, tying shoelaces looking up, evening glow, tired small smile"),
    ("livingroom_window", "long hair down",
     "simple cardigan, standing by living room window, looking outside, afternoon light, arms crossed, distant"),
    ("veranda_dry", "long hair pulled back casually",
     "simple t-shirt and skirt, on veranda hanging laundry, afternoon sun, looking aside, slight melancholy"),
]

NEG_BASE = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
            "cartoon, anime, illustration, painting, 3d render, cgi, "
            "nude, exposed, oversaturated, hdr, airbrushed, "
            "mutated hands, extra fingers, deformed, bad anatomy, "
            "watermark, signature, text, logo, existing celebrity, real person, "
            "makeup, frills, lace, ribbon, curly hair, wavy hair, "
            "bangs, bob cut, shoulder-length, hair ends at shoulders, "
            "long hair past waist, very long hair")

# 20 configs: (scene_idx, prompt_key, faceid_w, cfg, doll_strength, dt_strength)
CONFIGS = [
    (0,"A",0.5,8.0,0.0,0.2),(0,"A",0.4,8.0,0.0,0.2),
    (0,"A",0.3,8.0,0.0,0.2),(0,"A",0.2,8.0,0.0,0.2),
    (0,"A",0.4,10.0,0.0,0.2),
    (1,"B",0.4,8.0,0.0,0.2),(1,"B",0.4,10.0,0.0,0.2),
    (1,"B",0.4,12.0,0.0,0.2),(1,"B",0.3,10.0,0.0,0.2),
    (1,"B",0.3,8.0,0.0,0.2),
    (2,"C",0.4,8.0,0.0,0.0),(2,"C",0.4,8.0,0.15,0.2),
    (2,"C",0.3,8.0,0.0,0.2),(2,"C",0.4,10.0,0.0,0.2),
    (2,"C",0.3,10.0,0.15,0.0),
    (3,"A",0.2,10.0,0.0,0.0),(3,"A",0.4,12.0,0.0,0.2),
    (4,"B",0.3,10.0,0.15,0.0),
    (5,"A",0.4,8.0,0.0,0.2),(6,"A",0.2,12.0,0.0,0.0),
]

def upload_ref(path):
    with open(path,"rb") as f:
        r=requests.post(f"{BASE}/upload/image",files={"image":(os.path.basename(path),f,"image/png")},timeout=30)
    return r.json()["name"] if r.status_code==200 else None

def build_wf(seed, prompt, neg, ref_name, prefix, fw, cfg, doll, dt):
    p=prompt.replace('"','\\"'); n=neg.replace('"','\\"')
    wf={"1":{"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":CKPT}}}
    md="1"
    wf["1a"]={"class_type":"LoraLoader","inputs":{"model":["1",0],"clip":["1",1],
        "lora_name":"JapaneseDollLikeness_v15.safetensors","strength_model":doll,"strength_clip":doll}}
    md="1a"
    if dt>0:
        wf["2a"]={"class_type":"LoraLoader","inputs":{"model":[md,0],"clip":[md,1],
            "lora_name":"DetailTweaker.safetensors","strength_model":dt,"strength_clip":dt}}
        md="2a"
    wf["2"]={"class_type":"IPAdapterUnifiedLoaderFaceID","inputs":{"model":[md,0],"preset":"FACEID PLUS V2","lora_strength":0.5,"provider":"CPU"}}
    wf["3"]={"class_type":"LoadImage","inputs":{"image":ref_name}}
    wf["4"]={"class_type":"IPAdapterInsightFaceLoader","inputs":{"provider":"CPU","model_name":"buffalo_l"}}
    wf["5"]={"class_type":"IPAdapterFaceID","inputs":{"model":["2",0],"ipadapter":["2",1],"image":["3",0],
        "weight":fw,"weight_faceidv2":0.0,"weight_type":"linear","combine_embeds":"concat",
        "start_at":0.0,"end_at":1.0,"embeds_scaling":"V only","insightface":["4",0]}}
    wf["6"]={"class_type":"CLIPTextEncode","inputs":{"text":n,"clip":[md,1]}}
    wf["7"]={"class_type":"CLIPTextEncode","inputs":{"text":p,"clip":[md,1]}}
    wf["8"]={"class_type":"EmptyLatentImage","inputs":{"width":W,"height":H,"batch_size":1}}
    wf["9"]={"class_type":"KSampler","inputs":{"seed":seed,"steps":STEPS,"cfg":cfg,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["5",0],"positive":["7",0],"negative":["6",0],"latent_image":["8",0]}}
    wf["10"]={"class_type":"VAEDecode","inputs":{"samples":["9",0],"vae":["1",2]}}
    wf["11"]={"class_type":"SaveImage","inputs":{"filename_prefix":prefix,"images":["10",0]}}
    return wf

def gen_one(seed, prompt, neg, ref_name, prefix, fw, cfg, doll, dt):
    wf=build_wf(seed, prompt, neg, ref_name, prefix, fw, cfg, doll, dt)
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
                            url=f"{BASE}/view?{p}"; outpath=os.path.join(OUT,img["filename"])
                            resp=requests.get(url,timeout=60)
                            if len(resp.content)>1000:
                                with open(outpath,"wb") as f: f.write(resp.content)
                                print(f"  {prefix} OK ({len(resp.content)//1024}kb)")
                            else: print(f"  {prefix} EMPTY")
                    return
                elif st=="error": print(f"  {prefix} ERROR"); return
        except:
            if j==299: print(f"  {prefix} TIMEOUT")

print("Upload ref...")
ref_name=upload_ref(REF)

for i,(si,pk,fw,cfg,doll,dt) in enumerate(CONFIGS,1):
    seed=random.randint(1000000000,9999999999)
    sname, hair_d, clothes = SCENES[si]
    pp = P[pk]
    prompt = f"{pp['pos_prefix']}, {hair_d}, {clothes}, {pp['pos_aging']}"
    neg = f"{NEG_BASE}, {pp['neg_extra']}"
    tag = f"P{pk}_F{fw}_C{cfg}_D{doll}_DT{dt}"
    prefix = f"{CHAR}_{AGE}_{MODEL}_s{seed}_{sname}_{tag}"
    print(f"[{i}/20] s{seed} {sname} | {tag}")
    gen_one(seed, prompt, neg, ref_name, prefix, fw, cfg, doll, dt)
    time.sleep(0.3)
