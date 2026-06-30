"""
橘百合子18歳: seed 5977固定 × 10バリエーション (服・角度・ポーズ)
"""
import requests, json, time, urllib.request, os

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
LORA1, L1S = "JapaneseDollLikeness_v15.safetensors", 0.5
LORA2, L2S = "DetailTweaker.safetensors", 0.2
W, H, STEPS, CFG = 512, 768, 28, 7.0
SAMPLER, SCHEDULER = "dpmpp_2m", "karras"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\02_18歳_回想_新入社員"
os.makedirs(OUT, exist_ok=True)
SEED = 5977

NEG = ("EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), "
       "cartoon, anime, illustration, painting, 3d render, cgi, "
       "nude, exposed, oversaturated, hdr, plastic skin, airbrushed, "
       "duplicate person, mutated hands, extra fingers, deformed, bad anatomy, "
       "watermark, signature, text, logo, existing celebrity, real person, copyrighted character, "
       "makeup, frills, lace, ribbon, long hair, hair past ears, curly hair, wavy hair, "
       "low ponytail, long ponytail")

BASE_FACE = ("(masterpiece, best quality:1.2), 8k, RAW photo, "
             "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, "
             "18 year old japanese young woman, petite small frame, "
             "plain natural face, no makeup, t_yuriko_f")

VARIANTS = [
    {
        "name": "uniform_bob_stand",
        "hair": "short black bob haircut, hair ends at jawline",
        "clothes": "navy blazer with gold buttons, white blouse, knee-length navy skirt, classic japanese office lady uniform",
        "pose": "standing, hands at sides, full body, front view, facing camera, looking at viewer",
    },
    {
        "name": "uniform_tied_walk",
        "hair": "short hair pulled back in small ponytail at nape",
        "clothes": "navy blazer with gold buttons, white blouse, knee-length navy skirt, classic japanese office lady uniform, carrying simple handbag",
        "pose": "walking, mid-stride, three-quarter view, looking slightly to the side",
    },
    {
        "name": "cardigan_bob_sit",
        "hair": "short black bob haircut, hair ends at jawline",
        "clothes": "warm beige cardigan over cream top, brown knee-length skirt",
        "pose": "sitting on chair, front view, facing camera, looking at viewer, hands on lap",
    },
    {
        "name": "cardigan_tied_book",
        "hair": "short hair pulled back in small ponytail at nape",
        "clothes": "warm beige cardigan over cream top, brown knee-length skirt",
        "pose": "standing, holding a book, three-quarter view, looking down at book",
    },
    {
        "name": "knitsweater_bob_profile",
        "hair": "short black bob haircut, hair ends at jawline",
        "clothes": "rust-colored knit sweater, dark brown straight-leg pants",
        "pose": "leaning against wall, side view, profile, looking away",
    },
    {
        "name": "knitsweater_tied_pocket",
        "hair": "short hair pulled back in small ponytail at nape",
        "clothes": "rust-colored knit sweater, dark brown straight-leg pants",
        "pose": "standing, hands in pockets, front view, facing camera, looking at viewer",
    },
    {
        "name": "turtleneck_bob_lookup",
        "hair": "short black bob haircut, hair ends at jawline",
        "clothes": "cream turtleneck sweater, olive green A-line knee-length skirt",
        "pose": "standing, three-quarter view, looking up slightly, slight smile",
    },
    {
        "name": "turtleneck_tied_desk",
        "hair": "short hair pulled back in small ponytail at nape",
        "clothes": "cream turtleneck sweater, olive green A-line knee-length skirt",
        "pose": "sitting at desk, turning around, looking over shoulder at camera",
    },
    {
        "name": "vest_bob_read",
        "hair": "short black bob haircut, hair ends at jawline",
        "clothes": "light brown knit vest over white blouse, tan knee-length skirt",
        "pose": "profile view, reading a document in hands, standing",
    },
    {
        "name": "vest_tied_bag",
        "hair": "short hair pulled back in small ponytail at nape",
        "clothes": "light brown knit vest over white blouse, tan knee-length skirt",
        "pose": "front view, carrying a tote bag over shoulder, smiling slightly at camera",
    },
]

def gen_one(seed, prompt, neg, prefix):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LoraLoader", "inputs": {"model":["1",0],"clip":["1",1],"lora_name":LORA1,"strength_model":L1S,"strength_clip":L1S}},
        "9": {"class_type": "LoraLoader", "inputs": {"model":["2",0],"clip":["2",1],"lora_name":LORA2,"strength_model":L2S,"strength_clip":L2S}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip":["9",1]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip":["9",1]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width":W,"height":H,"batch_size":1}},
        "6": {"class_type": "KSampler", "inputs": {"seed":seed,"steps":STEPS,"cfg":CFG,"sampler_name":SAMPLER,"scheduler":SCHEDULER,"denoise":1.0,"model":["9",0],"positive":["3",0],"negative":["4",0],"latent_image":["5",0]}},
        "7": {"class_type": "VAEDecode", "inputs": {"samples":["6",0],"vae":["1",2]}},
        "8": {"class_type": "SaveImage", "inputs": {"filename_prefix":prefix,"images":["7",0]}},
    }
    try:
        r = requests.post(f"{BASE}/prompt", json={"prompt":wf}, timeout=30)
        r.raise_for_status()
        pid = r.json()["prompt_id"]
    except Exception as e:
        print(f"  {prefix} SUBMIT: {e}")
        return
    for j in range(120):
        time.sleep(2)
        try:
            h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
            if pid in h:
                st = h[pid]["status"]["status_str"]
                if st == "success":
                    for nid, node in h[pid]["outputs"].items():
                        for img in node.get("images",[]):
                            url = f"{BASE}/view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
                            out = os.path.join(OUT, img["filename"])
                            urllib.request.urlretrieve(url, out)
                            print(f"  {prefix} OK ({os.path.getsize(out)//1024}kb)")
                    return
                elif st == "error":
                    print(f"  {prefix} ERROR")
                    return
        except:
            if j == 119:
                print(f"  {prefix} TIMEOUT")
                return

for i, v in enumerate(VARIANTS, 1):
    prompt = f"{BASE_FACE}, {v['hair']}, {v['clothes']}, {v['pose']}"
    prefix = f"yuriko_s{SEED}_{v['name']}"
    print(f"[{i}/10] {prefix}")
    gen_one(SEED, prompt, NEG, prefix)
    time.sleep(0.3)
