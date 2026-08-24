# -*- coding: utf-8 -*-
"""プロローグ用 背景挿絵4枚生成"""
import json, time, urllib.request, io, os
from PIL import Image, ImageEnhance

SERVER = "http://100.112.59.35:18188"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_bg_images")
os.makedirs(OUT, exist_ok=True)
CKPT = "yayoi_mix.safetensors"
NEG = "text, watermark, signature, logo, anime, cartoon, illustration, painting, lowres, worst quality, low quality, deformed, bad anatomy, jpeg artifacts, frame, border, person face closeup"

JOBS = [
    ("bg01_street_night", 832, 552,
     "quiet japanese suburban residential street at night, warm orange streetlights, two-story wooden house with lit windows, cherry tree silhouettes, no people, cinematic atmosphere, photorealistic"),
    ("bg02_study_monitor", 832, 552,
     "japanese home office study room at night, multiple computer monitors displaying stock charts with green and red lines, dim desk lamp, coffee mug, empty chair, moody lighting, photorealistic"),
    ("bg03_family_dinner", 832, 552,
     "japanese family dinner table from slightly above, four place settings, purin pudding desserts, beer can, warm overhead light, cozy evening atmosphere, no people visible only hands and food, photorealistic"),
    ("bg04_house_lamp", 640, 800,
    "japanese living room at night viewed from sofa, warm floor lamp glow, kitchen doorway with soft light in background, quiet peaceful evening, no people, photorealistic"),
]

def gen(name, w, h, prompt):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"seed": 20260824 + hash(name) % 10000, "steps": 26, "cfg": 7.0,
              "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0,
              "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "prologue_bg/" + name}},
    }
    req = urllib.request.Request(SERVER + "/prompt",
        data=json.dumps({"prompt": wf}).encode(), headers={"Content-Type": "application/json"})
    pid = json.loads(urllib.request.urlopen(req, timeout=30).read())["prompt_id"]
    for _ in range(60):
        time.sleep(4)
        hist = json.loads(urllib.request.urlopen(SERVER + "/history/" + pid, timeout=30).read())
        if pid in hist:
            for nid, o in hist[pid].get("outputs", {}).items():
                if "images" in o:
                    im = o["images"][0]
                    q = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im.get("subfolder",""), "type": im.get("type","output")})
                    return urllib.request.urlopen(SERVER + "/view?" + q, timeout=60).read()
    raise RuntimeError("timeout")

ok = 0
for i, (name, w, h, prompt) in enumerate(JOBS):
    out_p = os.path.join(OUT, name + ".png")
    if os.path.exists(out_p):
        print(f"[{i+1}/4] skip {name}"); ok += 1; continue
    try:
        print(f"[{i+1}/4] {name}...", end=" ", flush=True)
        data = gen(name, w, h, prompt)
        im = Image.open(io.BytesIO(data)).convert("RGB")
        ratio = 1920 / im.width
        im = im.resize((1920, int(im.height * ratio)), Image.LANCZOS)
        im = ImageEnhance.Brightness(im).enhance(0.90)
        im.save(out_p, quality=95)
        print("OK"); ok += 1
    except Exception as e:
        print(f"FAIL: {e}")
print(f"\n{ok}/4 done")
