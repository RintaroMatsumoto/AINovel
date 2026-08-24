# -*- coding: utf-8 -*-
"""GoldenCross スロスク動画用 静止画一括生成（ComfyUI M1サーバー）"""
import json, time, urllib.request, urllib.parse, io, os, sys
from PIL import Image, ImageEnhance

SERVER = "http://100.112.59.35:18188"
OUT_DIR = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\GoldenCross\動画\images"
os.makedirs(OUT_DIR, exist_ok=True)

CKPT = "yayoi_mix.safetensors"
NEG = "text, watermark, signature, logo, anime, cartoon, illustration, painting, sketch, lowres, worst quality, low quality, deformed, bad anatomy, jpeg artifacts, frame, border"

JOBS = [
    ("img01_doll",        640, 800, "antique french bisque doll sitting alone, golden curly hair, blue glass eyes, floral dress, on dark wooden shelf, single spotlight from above, dust particles floating in light beam, melancholic, cinematic still life, photorealistic"),
    ("img02_goldcoins",   832, 552, "ten gold coins arranged in a row on an old wooden desk, warm lamp light, shallow depth of field, photorealistic still life"),
    ("img03_notebook",    640, 800, "worn brown notebook with faded sticky notes and coffee ring stains on wooden desk, dramatic side lighting, photorealistic close up"),
    ("img04_letters",     832, 552, "open wooden desk drawer containing folded old letters tied with string, dim room, nostalgic atmosphere, photorealistic"),
    ("img05_envelope",    832, 552, "white resignation envelope lying on office desk, morning light from large window, corporate bokeh background, photorealistic"),
    ("img06_train_night", 832, 552, "view from japanese commuter train window at night, river bridge, suburban lights streaking past, reflection on glass, melancholic, photorealistic"),
    ("img07_office_win",  832, 552, "japanese corporate office interior, large window overlooking green park, morning light, empty desks, photorealistic"),
    ("img08_house_night", 640, 800, "suburban japanese two-story wooden house at night, warm light glowing in upstairs window, quiet residential street, streetlamp, photorealistic"),
    ("img09_familyphoto", 640, 800, "printed family photograph standing upright on kitchen shelf, slightly out of focus subjects, warm home lighting, nostalgic, photorealistic"),
    ("img10_brown_env",   832, 552, "plain brown kraft paper envelope with postage stamp and printed address label, no handwriting, resting on top of home mailbox, overcast daylight, photorealistic"),
    ("img11_photos",      832, 552, "five small printed photographs spread on a wooden desk, blurred office scene in photos, overhead view, photorealistic"),
    ("img12_kitchen",     832, 552, "japanese kitchen counter at dusk, chopping board and knife silhouette, warm ceiling light, steam, photorealistic"),
    ("img13_fusuma",      640, 800, "closed japanese fusuma sliding doors seen from dim hallway, thin strip of warm light leaking underneath, photorealistic"),
    ("img14_police",      832, 552, "empty police station reception counter at night, cold fluorescent light, steel and linoleum, lonely atmosphere, photorealistic"),
    ("img15_teishoku",    832, 552, "small japanese diner counter with two tea cups and plates, warm lantern light, night, photorealistic"),
    ("img16_hotel_curtain",640, 800, "hotel room window with curtains slightly open, city lights bokeh at night, empty room corner, photorealistic"),
    ("img17_saxblue_room",640, 800, "small clean apartment room with light blue curtains, evening sunlight streaming in, simple furniture, nostalgic japanese interior, photorealistic"),
    ("img18_sea_lights",  832, 552, "fishing boat lights dotting dark sea at night viewed from japanese inn window, distant horizon, calm melancholic, photorealistic"),
    ("img19_hanabi_smoke",832, 552, "smoke lingering over riverbank after fireworks at night, hand holding small jewelry ring box in foreground, departing crowd bokeh, photorealistic"),
    ("img20_register",    832, 552, "supermarket checkout counter seen from store entrance, blurred clerk wearing green apron, fluorescent light, photorealistic"),
    ("img21_sink_ashes",  832, 552, "kitchen stainless steel sink drain with burnt paper ash fragments, water droplets, harsh morning daylight, overhead view, photorealistic"),
    ("img22_washitsu",    640, 800, "dark japanese tatami room, closed fusuma doors casting long shadows, single strip of light under door, emptiness, photorealistic"),
]

def queue(name, prompt, neg, w, h, seed):
    wf = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "5": {"class_type": "KSampler", "inputs": {"seed": seed, "steps": 26, "cfg": 7.0,
              "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": 1.0,
              "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]}},
        "6": {"class_type": "VAEDecode", "inputs": {"samples": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "SaveImage", "inputs": {"images": ["6", 0], "filename_prefix": "gcvid/" + name}},
    }
    req = urllib.request.Request(SERVER + "/prompt",
        data=json.dumps({"prompt": wf, "client_id": "gcvid"}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["prompt_id"]

def wait_and_fetch(pid):
    for _ in range(120):
        time.sleep(4)
        with urllib.request.urlopen(SERVER + "/history/" + pid, timeout=30) as r:
            hist = json.loads(r.read())
        if pid in hist:
            outs = hist[pid].get("outputs", {})
            for node_id, o in outs.items():
                if "images" in o:
                    img = o["images"][0]
                    q = urllib.parse.urlencode({"filename": img["filename"],
                        "subfolder": img.get("subfolder", ""), "type": img.get("type", "output")})
                    with urllib.request.urlopen(SERVER + "/view?" + q, timeout=60) as ir:
                        return ir.read()
    raise RuntimeError("timeout: " + pid)

def main():
    ok, fail = [], []
    for i, (name, w, h, prompt) in enumerate(JOBS, 1):
        out_path = os.path.join(OUT_DIR, name + ".png")
        if os.path.exists(out_path):
            print(f"[{i}/{len(JOBS)}] skip {name}")
            continue
        try:
            seed = 20260824 + i * 7919
            pid = queue(name, prompt, NEG, w, h, seed)
            print(f"[{i}/{len(JOBS)}] queued {name} ({pid})")
            data = wait_and_fetch(pid)
            im = Image.open(io.BytesIO(data)).convert("RGB")
            # 統一グレード：幅1080へ拡大＋軽い減光＋ビネット
            ratio = 1080 / im.width
            im = im.resize((1080, int(im.height * ratio)), Image.LANCZOS)
            im = ImageEnhance.Brightness(im).enhance(0.92)
            im = ImageEnhance.Color(im).enhance(0.88)
            im.save(out_path, quality=95)
            print(f"    saved {out_path}")
            ok.append(name)
        except Exception as e:
            print(f"    FAIL {name}: {e}")
            fail.append((name, str(e)))
        time.sleep(2)
    print(f"\n=== done ok={len(ok)} fail={len(fail)} ===")
    for n, e in fail:
        print("FAIL:", n, e)

if __name__ == "__main__":
    main()
