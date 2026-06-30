"""百合子34歳: シンプル爆上げ。CFGを振ってFaceID弱めてDetailTweaker除去"""
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

BASE_POS = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
            "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
            "japanese woman, 34 years old, married, mother of two, "
            "long straight black hair, hair reaches middle of back, "
            "plain natural face, no makeup")

AGING = ("worn exhausted tired mother, visible aging signs on face, "
         "deep dark circles under eyes, heavy eye bags, "
         "sunken tired eyes, hollow gaze, crows feet, "
         "rough dry skin texture, dull lifeless complexion, "
         "gaunt hollow cheeks, sagging skin around jaw, "
         "years of stress and hidden suffering in eyes, "
         "unflattering aging, weathered face")

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, ribbon, curly hair, wavy hair, "
       "bangs, bob cut, shoulder-length, hair ends at shoulders, "
       "long hair past waist, very long hair, "
       "young, 20s, teenager, fresh, firm, smooth elastic skin, perfect skin, "
       "glowing skin, beautiful, pretty, cute, attractive, glamorous, flawless, "
       "bouncy, radiant, clear skin, youthful, energetic, healthy glow, "
       "refreshed, well rested, porcelain skin, soft skin, dewy skin, "
       "plump skin, supple skin, bright skin, hydrated")

SCENE = ("simple shirt, at dining table with coffee cup, "
         "side angle 45 degrees, staring at coffee, "
         "midday, alone, still")

# 5 configs: CFG 8~16, FaceID 0.2~0.4, DetailTweaker 0 or 0.2
CONFIGS = [
    (8.0, 0.3, 0.0, "cfg8_f03_noDT"),
    (10.0, 0.3, 0.0, "cfg10_f03_noDT"),
    (12.0, 0.3, 0.0, "cfg12_f03_noDT"),
    (12.0, 0.2, 0.0, "cfg12_f02_noDT"),
    (16.0, 0.2, 0.0, "cfg16_f02_noDT"),
]

def upload_ref(path):
    with open(path,"rb") as f:
        r=requests.post(f"{BASE}/upload/image",files={"image":(os.path.basename(path),f,"image/png")},timeout=30)
    return r.json()["name"] if r.status_code==200 else None

def build_wf(seed, prompt, neg, ref_name, prefix, cfg, fw):
    p=prompt.replace('"','\\"'); n=neg.replace('"','\\"')
    wf={"1":{"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":CKPT}}}
    wf["2"]={"class_type":"IPAdapterUnifiedLoaderFaceID","inputs":{"model":["1",0],"preset":"FACEID PLUS V2","lora_strength":0.5,"provider":"CPU"}}
    wf["3"]={"class_type":"LoadImage","inputs":{"image":ref_name}}
    wf["4"]={"class_type":"IPAdapterInsightFaceLoader","inputs":{"provider":"CPU","model_name":"buffalo_l"}}
    wf["5"]={"class_type":"IPAdapterFaceID","inputs":{"model":["2",0],"ipadapter":["2",1],"image":["3",0],
        "weight":fw,"weight_faceidv2":0.0,"weight_type":"linear","combine_embeds":"concat",
        "start_at":0.0,"end_at":1.0,"embeds_scaling":"V only","insightface":["4",0]}}
    wf["6"]={"class_type":"CLIPTextEncode","inputs":{"text":n,"clip":["1",1]}}
    wf["7"]={"class_type":"CLIPTextEncode","inputs":{"text":p,"clip":["1",1]}}
    wf["8"]={"class_type":"EmptyLatentImage","inputs":{"width":W,"height":H,"batch_size":1}}
    wf["9"]={"class_type":"KSampler","inputs":{"seed":seed,"steps":STEPS,"cfg":cfg,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["5",0],"positive":["7",0],"negative":["6",0],"latent_image":["8",0]}}
    wf["10"]={"class_type":"VAEDecode","inputs":{"samples":["9",0],"vae":["1",2]}}
    wf["11"]={"class_type":"SaveImage","inputs":{"filename_prefix":prefix,"images":["10",0]}}
    return wf

def gen_one(seed, prompt, neg, ref_name, prefix, cfg, fw):
    wf=build_wf(seed, prompt, neg, ref_name, prefix, cfg, fw)
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
                            else:
                                print(f"  {prefix} EMPTY ({len(resp.content)}b)")
                    return
                elif st=="error": print(f"  {prefix} ERROR"); return
        except:
            if j==299: print(f"  {prefix} TIMEOUT")

print("Upload ref...")
ref_name=upload_ref(REF)

for i,(cfg, fw, dl, tag) in enumerate(CONFIGS,1):
    seed=random.randint(1000000000,9999999999)
    prompt=f"{BASE_POS}, {SCENE}, {AGING}"
    prefix=f"{CHAR}_{AGE}_{MODEL}_s{seed}_dining_{tag}"
    print(f"[{i}/5] s{seed} CFG={cfg} FaceID={fw} DetailTweaker={dl}")
    gen_one(seed, prompt, NEG, ref_name, prefix, cfg, fw)
    time.sleep(0.5)
