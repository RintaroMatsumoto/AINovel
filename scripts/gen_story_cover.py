"""
ゴールデンクロス 表紙生成
======================
M1 ComfyUI (100.112.59.35:18188) + RealVisXL V5
1024x1536 portrait book cover, 4 volumes x 2 variants
"""
import requests, json, time, urllib.request, os, sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

BASE = "http://100.112.59.35:18188"
CHECKPOINT = "RealVisXL_V5.0_fp16.safetensors"
OUTPUT_DIR = r"C:\Users\GoldRush\Documents\MyProject\AINovel\covers\ゴールデンクロス"
os.makedirs(OUTPUT_DIR, exist_ok=True)

WIDTH = 1024
HEIGHT = 1536
STEPS = 30
CFG = 5.0
SAMPLER = "dpmpp_2m"
SCHEDULER = "karras"

NEGATIVE = (
    "cartoon, anime, illustration, painting, 3d render, cgi, "
    "text, watermark, signature, logo, "
    "nsfw, nude, exposed, "
    "deformed, bad anatomy, mutated hands, extra fingers, "
    "oversaturated, blurry, low quality"
)

# 4巻の表紙プロンプト（英文）
COVERS = [
    {
        "vol": "FIRE",
        "prefix": "goldencross_vol1_fire",
        "positive": (
            "professional book cover, digital painting, portrait 2:3 ratio, "
            "a 40 year old Japanese businessman in dark blue suit, standing alone, back view, "
            "looking at golden sunset sky, stock market candlestick charts floating in air, "
            "warm golden and amber tones, dramatic lighting from above, "
            "moody contemplative atmosphere, high detail, photorealistic, "
            "cinematic composition, shallow depth of field"
        )
    },
    {
        "vol": "デッドクロス",
        "prefix": "goldencross_vol2_deadcross",
        "positive": (
            "professional book cover, digital painting, portrait 2:3 ratio, "
            "a young 16 year old Japanese girl with short dark hair, standing alone at night, "
            "neon lit Kabukicho street background, rain falling, wet asphalt reflecting red and blue lights, "
            "dark crimson and black color scheme, dramatic noir lighting, "
            "gritty urban atmosphere, high detail, photorealistic, "
            "cinematic composition, dutch angle"
        )
    },
    {
        "vol": "ブレイクアウト",
        "prefix": "goldencross_vol3_breakout",
        "positive": (
            "professional book cover, digital painting, portrait 2:3 ratio, "
            "a 30 year old Japanese man in a wheelchair, looking up at bright blue sky, "
            "breaking through dark clouds, sun rays piercing through, "
            "blue and white color scheme, dramatic backlighting, "
            "hopeful triumphant atmosphere, high detail, photorealistic, "
            "cinematic composition, low angle shot"
        )
    },
    {
        "vol": "ロスカット",
        "prefix": "goldencross_vol4_losscut",
        "positive": (
            "professional book cover, digital painting, portrait 2:3 ratio, "
            "silhouette of a Japanese woman in white dress, standing by window, "
            "scattered cherry blossom petals floating, soft morning light, "
            "a handwritten letter on a wooden table in foreground, "
            "pale grey and soft white color scheme, ethereal dreamlike lighting, "
            "melancholic peaceful atmosphere, high detail, photorealistic, "
            "cinematic composition"
        )
    },
]

# 各表紙2枚ずつ生成（seed違い）
SEEDS = [3001, 3002]

print(f"Target: {BASE}")
print(f"Model: {CHECKPOINT}")
print(f"Output: {OUTPUT_DIR}")
print(f"Size: {WIDTH}x{HEIGHT}, Steps: {STEPS}, CFG: {CFG}")
print()

for cover in COVERS:
    vol = cover["vol"]
    prefix = cover["prefix"]
    positive = cover["positive"]
    
    for seed in SEEDS:
        full_prefix = f"{prefix}_seed{seed}"
        print(f"[{vol}] seed={seed} submitting...")
        
        wf = {
            "1": {"class_type": "CheckpointLoaderSimple",
                  "inputs": {"ckpt_name": CHECKPOINT}},
            "2": {"class_type": "CLIPTextEncode",
                  "inputs": {"text": positive, "clip": ["1", 1]}},
            "3": {"class_type": "CLIPTextEncode",
                  "inputs": {"text": NEGATIVE, "clip": ["1", 1]}},
            "4": {"class_type": "EmptyLatentImage",
                  "inputs": {"width": WIDTH, "height": HEIGHT, "batch_size": 1}},
            "5": {"class_type": "KSampler",
                  "inputs": {"seed": seed, "steps": STEPS, "cfg": CFG,
                             "sampler_name": SAMPLER, "scheduler": SCHEDULER,
                             "denoise": 1.0,
                             "model": ["1", 0], "positive": ["2", 0],
                             "negative": ["3", 0], "latent_image": ["4", 0]}},
            "6": {"class_type": "VAEDecode",
                  "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
            "7": {"class_type": "SaveImage",
                  "inputs": {"filename_prefix": full_prefix, "images": ["6", 0]}},
        }
        
        try:
            r = requests.post(f"{BASE}/prompt", json={"prompt": wf}, timeout=15)
            r.raise_for_status()
            pid = r.json()["prompt_id"]
        except Exception as e:
            print(f"  SUBMIT ERROR: {e}")
            continue
        
        done = False
        for j in range(120):
            time.sleep(3)
            try:
                h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
                if pid in h:
                    st = h[pid]["status"]["status_str"]
                    if st == "success":
                        outputs = h[pid]["outputs"]
                        for nid, node in outputs.items():
                            for img in node.get("images", []):
                                url = f"{BASE}/view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
                                out_path = os.path.join(OUTPUT_DIR, img["filename"])
                                urllib.request.urlretrieve(url, out_path)
                                size_kb = os.path.getsize(out_path) // 1024
                                print(f"  OK: {img['filename']} ({size_kb}KB)")
                        done = True
                        break
                    elif st == "error":
                        print(f"  JOB ERROR")
                        done = True
                        break
            except Exception as e:
                if j == 119:
                    print(f"  TIMEOUT")
        
        time.sleep(1)

print()
print("=" * 60)
print("完了")
print(f"Output dir: {OUTPUT_DIR}")
files = list(Path(OUTPUT_DIR).glob("*.png"))
print(f"Generated: {len(files)} files")
