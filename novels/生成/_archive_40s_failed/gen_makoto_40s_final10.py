"""誠40歳: cafe_street確定ベース 10枚"""
import requests, json, time, urllib.request, os, random

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
W, H, STEPS = 512, 768, 28
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
CFG = 9.5
CHAR_NAME = "makoto"
AGE = "40"
MODEL_NAME = "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\02_40歳_退職前"
os.makedirs(OUT, exist_ok=True)

REF_IMG = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\02_40歳_退職前\makoto_40_yayoi_mix_fid4_cfg9_s6250727949_cafe_street_00001_.png"

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, jewelry, earring, necklace, "
       "feminine, woman, female features, androgynous, "
       "soft face, delicate, pretty, girly, effeminate, ambiguous gender, "
       "younger than 20, teenager, "
       "curly hair, wavy hair, colored hair, long hair, "
       "pompadour, quiff, slicked back, heavy wax, excessive volume, "
       "sharp sideburns, host style, flashy hair, gel hair, spiky hair, "
       "extreme two block, undercut, "
       "beard, full beard, long stubble, goatee, facial hair, "
       "black suit, funeral, mourning")

HAIR = "short neatly combed salt and pepper hair, natural side part, slight gray at temples, subtle silver strands"
GLASSES = "(silver thin metal frame glasses:1.1)"

SCENES = [
    ("suit_front", "navy suit, white shirt, dark red tie, front view, standing, looking at camera, calm professional"),
    ("suit_desk", "white shirt, navy vest, no jacket, sitting at desk, reading document, focused"),
    ("suit_hallway", "navy suit, white shirt, burgundy tie, profile view, walking with briefcase, determined"),
    ("suit_window", "navy jacket, white shirt, tie loosened, standing by window, looking outside, tired"),
    ("suit_meeting", "navy suit, white shirt, red tie, sitting at conference table, listening, notebook"),
    ("casual_sofa", "white button shirt, no tie, casual pants, sitting on sofa, reading, relaxed"),
    ("casual_cafe", "white shirt, casual jacket, no tie, sitting at cafe with coffee, looking aside"),
    ("casual_street", "navy overcoat, scarf, no suit visible, walking on street, hands in pockets, cold"),
    ("casual_home", "simple white t-shirt, casual pants, standing in kitchen, pouring coffee, morning"),
    ("casual_evening", "navy suit, loosened tie, coat over arm, on evening street, tired commute"),
]

def upload_ref():
    with open(REF_IMG, "rb") as f:
        try:
            r=requests.post(f"{BASE}/upload/image", files={"image":("makoto_40_ref.png",f,"image/png")}, timeout=30)
            r.raise_for_status(); return r.json()["name"]
        except: return None

def gen_one(seed, prompt, neg, ref_name, prefix):
    wf = {
        "1":{"class_type":"CheckpointLoaderSimple","inputs":{"ckpt_name":CKPT}},
        "2":{"class_type":"IPAdapterUnifiedLoaderFaceID","inputs":{"model":["1",0],"preset":"FACEID PLUS V2","lora_strength":0.0,"provider":"CPU"}},
        "3":{"class_type":"LoadImage","inputs":{"image":ref_name}},
        "4":{"class_type":"IPAdapterInsightFaceLoader","inputs":{"provider":"CPU","model_name":"buffalo_l"}},
        "5":{"class_type":"IPAdapterFaceID","inputs":{"model":["2",0],"ipadapter":["2",1],"image":["3",0],"weight":0.4,"weight_faceidv2":0.0,"weight_type":"linear","combine_embeds":"concat","start_at":0.0,"end_at":1.0,"embeds_scaling":"V only","insightface":["4",0]}},
        "6":{"class_type":"CLIPTextEncode","inputs":{"text":neg,"clip":["1",1]}},
        "7":{"class_type":"CLIPTextEncode","inputs":{"text":prompt,"clip":["1",1]}},
        "8":{"class_type":"EmptyLatentImage","inputs":{"width":W,"height":H,"batch_size":1}},
        "9":{"class_type":"KSampler","inputs":{"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["5",0],"positive":["7",0],"negative":["6",0],"latent_image":["8",0]}},
        "10":{"class_type":"VAEDecode","inputs":{"samples":["9",0],"vae":["1",2]}},
        "11":{"class_type":"SaveImage","inputs":{"filename_prefix":prefix,"images":["10",0]}},
    }
    try:
        r=requests.post(f"{BASE}/prompt",json={"prompt":wf},timeout=30)
        r.raise_for_status(); pid=r.json()["prompt_id"]
    except Exception as e: print(f"  {prefix} SUBMIT: {e}"); return
    for j in range(120):
        time.sleep(2)
        try:
            h=requests.get(f"{BASE}/history/{pid}",timeout=10).json()
            if pid in h and h[pid]["status"]["status_str"]=="success":
                for nid,node in h[pid]["outputs"].items():
                    for img in node.get("images",[]):
                        url=f"{BASE}/view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
                        out=os.path.join(OUT,img["filename"])
                        urllib.request.urlretrieve(url,out)
                        print(f"  {prefix} OK ({os.path.getsize(out)//1024}kb)")
                return
            elif pid in h and h[pid]["status"]["status_str"]=="error":
                print(f"  {prefix} ERROR"); return
        except:
            if j==119: print(f"  {prefix} TIMEOUT")

print("誠40歳 cafe_street確定ベース 10枚...")
ref_name = upload_ref()
if not ref_name: print("ABORT"); exit(1)

for i,(tag,scene) in enumerate(SCENES,1):
    seed=random.randint(1000000000,9999999999)
    prompt=(f"(masterpiece, best quality:1.2), 8k, RAW photo, "
            f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
            f"japanese man, in his 40s, section manager, salaryman, "
            f"masculine face, strong jawline, sharp features, clean shaven, "
            f"{HAIR}, {GLASSES}, {scene}")
    prefix=f"{CHAR_NAME}_{AGE}_{MODEL_NAME}_fid4_cfg9_s{seed}_{tag}"
    print(f"[{i}/10] {tag}")
    gen_one(seed,prompt,NEG,ref_name,prefix)
    time.sleep(0.5)
print("完了。")
