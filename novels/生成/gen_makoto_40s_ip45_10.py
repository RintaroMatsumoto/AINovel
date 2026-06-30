"""誠40歳退職前: IPAdapterのみ + weightアップ 10枚
参照: cafe_street s6250727949
改善: weight 0.35→0.45 / weight_type "standard"
"""
import requests, json, time, urllib.request, os, random, urllib.parse

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
W, H, STEPS = 512, 768, 28
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
IPW, CFG = 0.45, 7.5
CHAR, AGE, MODEL = "makoto", "40", "yayoi_mix"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\02_40歳_退職前\採用"
os.makedirs(OUT, exist_ok=True)

REF = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\02_40歳_退職前\採用\makoto_40_yayoi_mix_fid4_cfg9_s6250727949_cafe_street_00001_.png"

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, airbrushed, "
       "mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, "
       "makeup, frills, lace, jewelry, earring, necklace, "
       "feminine, woman, female features, androgynous, "
       "soft face, delicate, pretty, girly, effeminate, ambiguous gender, "
       "curly hair, wavy hair, colored hair, long hair, "
       "pompadour, quiff, slicked back, heavy wax, excessive volume, "
       "sharp sideburns, host style, flashy hair, gel hair, spiky hair, "
       "extreme two block, undercut, "
       "beard, full beard, long stubble, goatee, facial hair, "
       "black suit, funeral, mourning, "
       "young, smooth skin, radiant, fresh-faced, "
       "glowing, vibrant, energetic, healthy, "
       "different person, face changed, identity change")

VARIANTS = [
    ("suit_front", "navy suit, white shirt, dark red tie", "front view, standing in office, looking at camera, hands at sides"),
    ("suit_threeq", "navy suit, white shirt, red tie", "three-quarter view, standing, looking slightly away, neutral"),
    ("suit_desk", "white shirt, navy vest, no jacket, tie loosened", "sitting at desk, reading documents, focused tired gaze"),
    ("suit_meeting", "navy suit, white shirt, red tie", "sitting at conference table, hands clasped, listening expression"),
    ("suit_hallway", "navy suit, red tie, briefcase", "walking in hallway, profile, mid-stride, tired commute"),
    ("suit_elevator", "navy suit, white shirt, red tie", "standing in elevator, hands at sides, looking ahead, tired"),
    ("casual_cafe", "white shirt, casual jacket, no tie, coffee cup", "sitting at cafe table, looking aside, afternoon"),
    ("casual_evening", "navy suit, loosened tie, coat over arm", "on evening street, tired after work, dim light"),
    ("casual_home", "white t-shirt, casual pants", "standing in kitchen, pouring coffee, morning"),
    ("casual_commute", "navy overcoat, scarf, suit underneath", "on train platform, waiting, looking at phone"),
]

def upload_ref():
    with open(REF, "rb") as f:
        try:
            r = requests.post(f"{BASE}/upload/image", files={"image": ("makoto_40_ref.png", f, "image/png")}, timeout=30)
            r.raise_for_status()
            return r.json()["name"]
        except Exception as e:
            print(f"Upload failed: {e}")
            return None

def gen_one(seed, prompt, neg, ref_name, prefix):
    esc_p = prompt.replace('"', '\\"')
    esc_n = neg.replace('"', '\\"')
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "IPAdapterUnifiedLoader", "inputs": {"model":["1",0], "preset":"STANDARD (medium strength)"}},
        "3": {"class_type": "LoadImage", "inputs": {"image": ref_name}},
        "4": {"class_type": "IPAdapter", "inputs": {"model":["2",0], "ipadapter":["2",1], "image":["3",0], "weight":IPW, "start_at":0.0, "end_at":1.0, "weight_type":"standard"}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"text": esc_n, "clip":["1",1]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": esc_p, "clip":["1",1]}},
        "7": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "8": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["4",0], "positive":["6",0], "negative":["5",0], "latent_image":["7",0]}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples":["8",0], "vae":["1",2]}},
        "10": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix, "images":["9",0]}},
    }
    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status()
        pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  {prefix} SUBMIT: {e}"); return
    for j in range(300):
        time.sleep(2)
        try:
            h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
            if pid in h:
                st = h[pid]["status"]["status_str"]
                if st == "success":
                    for nid, node in h[pid]["outputs"].items():
                        for img in node.get("images",[]):
                            params = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img["subfolder"], "type": img["type"]})
                            url = f"{BASE}/view?{params}"
                            outpath = os.path.join(OUT, img["filename"])
                            resp = requests.get(url, timeout=60)
                            if len(resp.content) > 1000:
                                with open(outpath, "wb") as f: f.write(resp.content)
                                print(f"  {prefix} OK ({len(resp.content)//1024}kb)")
                            else:
                                print(f"  {prefix} EMPTY ({len(resp.content)}b)")
                    return
                elif st == "error":
                    print(f"  {prefix} ERROR"); return
        except:
            if j == 299: print(f"  {prefix} TIMEOUT")

print("誠40歳: IPAdapter 0.45 standard 10枚...")
ref_name = upload_ref()
if not ref_name:
    print("ABORT"); exit(1)

for i, (tag, clothes, pose) in enumerate(VARIANTS, 1):
    seed = random.randint(1000000000, 9999999999)
    prompt = (f"(masterpiece, best quality:1.2), 8k, RAW photo, "
              f"(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
              f"japanese man, in his 40s, section manager, salaryman, "
              f"masculine face, strong jawline, sharp features, clean shaven, "
              f"natural salt and pepper hair, neatly combed side part, "
              f"slight gray at temples, subtle silver strands, "
              f"(silver thin metal frame glasses:1.1), "
              f"tired eyes, weary gaze, exhausted expression, "
              f"dark circles under eyes, slight hollow under eyes, "
              f"subdued expression, quiet weariness, experienced, "
              f"carries weight of years, tired at work, "
              f"{clothes}, {pose}")
    prefix = f"{CHAR}_{AGE}_{MODEL}_ip{IPW}_cfg{CFG}_s{seed}_{tag}"
    print(f"[{i}/10] {tag}")
    gen_one(seed, prompt, NEG, ref_name, prefix)
    time.sleep(0.3)
print("完了。")
