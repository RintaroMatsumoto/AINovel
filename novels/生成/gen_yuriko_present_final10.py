"""百合子34歳: CFG10.0確定、PBプロンプト、10バリエーション（髪型×服装×表情×角度）"""
import requests, json, time, os, random, urllib.parse, glob

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
W, H, STEPS = 512, 768, 28
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
FW, CFG, DOLL, DT = 0.3, 10.0, 0.0, 0.2
CHAR, AGE, MODEL = "yuriko", "34", "yayoi_mix"
PK = "B"  # prompt key
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\01_34歳_現在_主婦"
os.makedirs(OUT, exist_ok=True)

novels_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
fm = glob.glob(os.path.join(novels_dir, "novels", "**", "yuriko_face_s5977_00001_.png"), recursive=True)
REF = fm[0]; print(f"Ref: {REF}")

PREFIX = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
          "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
          "34-years-old, mature woman, thirties, "
          "long straight black hair, "
          "plain natural face, no makeup")

AGING = ("mother of two, experienced tired gaze, "
         "distant thoughtful expression, quiet weariness, "
         "natural aging around eyes, subdued expression")

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, ribbon, curly hair, wavy hair, "
       "bangs, bob cut, shoulder-length, hair ends at shoulders, "
       "long hair past waist, very long hair, "
       "young, teen, adolescent, childish, "
       "cute, kawaii, innocent, "
       "glowing skin, radiant, fresh-faced")

VARIANTS = [
    # name, hair_detail, clothes, pose_expression
    ("lowpony_window",
     "long hair tied in low ponytail, some strands loose",
     "worn grey cardigan over simple white shirt, dark knee-length skirt",
     "standing by window, profile view, looking outside at rain, "
     "arms hugging self slightly, afternoon gray light"),
    ("bun_bathroom",
     "messy bun at back of head, loose strands",
     "plain white tank top, comfortable old beige pants",
     "in bathroom before mirror, tying hair up, "
     "morning, tired eyes meeting own reflection, slight pause"),
    ("loose_childroom",
     "long hair down, slightly messy",
     "faded navy sweatshirt, old home pants",
     "sitting on floor outside children's room door, leaning against wall, "
     "listening to quiet inside, worried distant look, dim hallway"),
    ("halfup_livingroom",
     "half-up hairstyle, remaining hair down",
     "soft gray sweater, simple beige home skirt",
     "sitting on sofa with photo album on lap, "
     "looking down at open page, one hand touching photo, "
     "natural window light, three-quarter angle"),
    ("braid_kitchen",
     "loose side braid over shoulder",
     "apron over simple navy dress, rolled-up sleeves",
     "in kitchen making bento, looking down at hands working, "
     "morning light, slight tired smile, focused on task"),
    ("headband_bedroom",
     "hair down with soft headband",
     "old worn t-shirt as pajama, loose home pants",
     "lying on bed looking at ceiling, "
     "one arm behind head, morning light, blank expression"),
    ("sidepony_hallway",
     "low side ponytail, draped over left shoulder",
     "beige trench coat over simple shirt, about to go out",
     "at genkan putting on coat, turning to look back, "
     "door half open, outside light, about to leave"),
    ("chignon_desk",
     "loose chignon at nape",
     "simple knit sweater, reading glasses",
     "sitting at low desk with household accounts, "
     "calculator in hand, profile view, focused tired squint, desk lamp"),
    ("loose_window2",
     "long hair down",
     "dark blue yukata-style home robe, obi loosely tied",
     "standing at open window, one hand on frame, "
     "looking at evening sky, profile, cool wind, quiet solitude"),
    ("scrunchy_veranda",
     "messy ponytail with scrunchy",
     "faded t-shirt, worn shorts, barefoot",
     "on veranda, leaning on railing, looking at neighborhood, "
     "late afternoon, slight breeze, hands resting, empty gaze"),
]

def upload_ref(path):
    with open(path,"rb") as f:
        r=requests.post(f"{BASE}/upload/image",files={"image":(os.path.basename(path),f,"image/png")},timeout=30)
    return r.json()["name"] if r.status_code==200 else None

def build_wf(seed, prompt, neg, ref_name, prefix):
    p=prompt.replace('"','\\"'); n=neg.replace('"','\\"')
    doll_strength,doll_strength_clip=DOLL,DOLL
    wf={"1":{"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":CKPT}}}
    wf["1a"]={"class_type":"LoraLoader","inputs":{"model":["1",0],"clip":["1",1],
        "lora_name":"JapaneseDollLikeness_v15.safetensors","strength_model":doll_strength,"strength_clip":doll_strength_clip}}
    md="1a"
    if DT>0:
        wf["2a"]={"class_type":"LoraLoader","inputs":{"model":[md,0],"clip":[md,1],
            "lora_name":"DetailTweaker.safetensors","strength_model":DT,"strength_clip":DT}}
        md="2a"
    wf["2"]={"class_type":"IPAdapterUnifiedLoaderFaceID","inputs":{"model":[md,0],"preset":"FACEID PLUS V2","lora_strength":0.5,"provider":"CPU"}}
    wf["3"]={"class_type":"LoadImage","inputs":{"image":ref_name}}
    wf["4"]={"class_type":"IPAdapterInsightFaceLoader","inputs":{"provider":"CPU","model_name":"buffalo_l"}}
    wf["5"]={"class_type":"IPAdapterFaceID","inputs":{"model":["2",0],"ipadapter":["2",1],"image":["3",0],
        "weight":FW,"weight_faceidv2":0.0,"weight_type":"linear","combine_embeds":"concat",
        "start_at":0.0,"end_at":1.0,"embeds_scaling":"V only","insightface":["4",0]}}
    wf["6"]={"class_type":"CLIPTextEncode","inputs":{"text":n,"clip":[md,1]}}
    wf["7"]={"class_type":"CLIPTextEncode","inputs":{"text":p,"clip":[md,1]}}
    wf["8"]={"class_type":"EmptyLatentImage","inputs":{"width":W,"height":H,"batch_size":1}}
    wf["9"]={"class_type":"KSampler","inputs":{"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["5",0],"positive":["7",0],"negative":["6",0],"latent_image":["8",0]}}
    wf["10"]={"class_type":"VAEDecode","inputs":{"samples":["9",0],"vae":["1",2]}}
    wf["11"]={"class_type":"SaveImage","inputs":{"filename_prefix":prefix,"images":["10",0]}}
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
                            url=f"{BASE}/view?{p}"; outpath=os.path.join(OUT,img["filename"])
                            resp=requests.get(url,timeout=60)
                            if len(resp.content)>1000:
                                with open(outpath,"wb") as f: f.write(resp.content)
                                print(f"  {prefix} OK ({len(resp.content)//1024}kb)")
                            else: print(f"  {prefix} EMPTY ({len(resp.content)}b)")
                    return
                elif st=="error": print(f"  {prefix} ERROR"); return
        except:
            if j==299: print(f"  {prefix} TIMEOUT")

print("Upload ref...")
ref_name=upload_ref(REF)

for i,(name,hair,clothes,pose) in enumerate(VARIANTS,1):
    seed=random.randint(1000000000,9999999999)
    prompt=f"{PREFIX}, {hair}, {clothes}, {pose}, {AGING}"
    prefix=f"{CHAR}_{AGE}_{MODEL}_s{seed}_{name}"
    print(f"[{i}/10] s{seed} {name}")
    gen_one(seed,prompt,NEG,ref_name,prefix)
    time.sleep(0.3)
