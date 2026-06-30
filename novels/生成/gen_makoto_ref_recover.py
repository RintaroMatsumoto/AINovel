"""誠24歳: 参照顔 sidepart_a4 再生成（seed 1193774 完全再現）"""
import requests, json, time, urllib.request, os

BASE = "http://100.112.59.35:18188"
CKPT = "yayoi_mix.safetensors"
W, H, STEPS = 512, 768, 28
CFG, SAMPLER, SCHEDULER = 7.0, "dpmpp_2m", "karras"
SEED = 1193774
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘誠\01_24歳_社会人\採用"
os.makedirs(OUT, exist_ok=True)

NEG = "EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), " \
      "cartoon, anime, illustration, painting, 3d render, cgi, " \
      "nude, exposed, oversaturated, hdr, airbrushed, " \
      "mutated hands, extra fingers, deformed, bad anatomy, " \
      "watermark, signature, text, logo, existing celebrity, real person, " \
      "makeup, frills, lace, jewelry, earring, necklace, " \
      "glasses, spectacles, eyewear, " \
      "beard, stubble, facial hair, " \
      "feminine, woman, female features, androgynous, ambiguous gender, " \
      "soft face, delicate, pretty, girly, effeminate, " \
      "younger than 20, teenager, " \
      "curly hair, wavy hair, colored hair, long hair, " \
      "pompadour, quiff, slicked back, heavy wax, excessive volume, " \
      "sharp sideburns, host style, flashy hair, gel hair, spiky hair, " \
      "extreme two block, undercut"

POS = "(masterpiece, best quality:1.2), 8k, RAW photo, " \
      "(Realistic, hyper realistic, photorealistic:1.3), ultra detailed, " \
      "24 year old japanese man, mid 20s, salaryman, " \
      "masculine face, strong jawline, sharp features, no glasses, " \
      "natural side parted short hair, 70-30 side part, " \
      "late 2000s japanese salaryman hairstyle, " \
      "neat side part, classic office man haircut, conservative professional, " \
      "white shirt, loosened tie, jacket off, " \
      "sitting at conference table, leaning back, " \
      "attentive relaxed expression, " \
      "meeting room, notepad, water glass"

wf = {
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
    "2": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
    "3": {"class_type": "CLIPTextEncode", "inputs": {"text": POS, "clip": ["1", 1]}},
    "4": {"class_type": "EmptyLatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
    "5": {"class_type": "KSampler", "inputs": {"seed": SEED, "steps": STEPS, "cfg": CFG, "sampler_name": SAMPLER, "scheduler": SCHEDULER, "denoise": 1.0, "model": ["1", 0], "positive": ["3", 0], "negative": ["2", 0], "latent_image": ["4", 0]}},
    "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
    "7": {"class_type": "SaveImage", "inputs": {"filename_prefix": f"makoto_24_yayoi_mix_s{SEED}_sidepart_a4", "images": ["6", 0]}},
}

print("Generating sidepart_a4 (seed 1193774)...")
try:
    r = requests.post(f"{BASE}/prompt", json={"prompt": wf}, timeout=30)
    r.raise_for_status()
    pid = r.json()["prompt_id"]
except Exception as e:
    print(f"SUBMIT failed: {e}")
    exit(1)

for j in range(120):
    time.sleep(2)
    try:
        h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
        if pid in h:
            if h[pid]["status"]["status_str"] == "success":
                for nid, node in h[pid]["outputs"].items():
                    for img in node.get("images", []):
                        url = f"{BASE}/view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
                        out = os.path.join(OUT, img["filename"])
                        urllib.request.urlretrieve(url, out)
                        print(f"OK ({os.path.getsize(out)//1024}kb) -> {out}")
                exit(0)
            elif h[pid]["status"]["status_str"] == "error":
                print("ERROR"); exit(1)
    except:
        if j == 119: print("TIMEOUT"); exit(1)
