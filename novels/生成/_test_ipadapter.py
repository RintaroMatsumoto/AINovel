import requests, json, time, os, urllib.request

BASE = "http://100.112.59.35:18188"
REF = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\02_18歳_回想_新入社員\yuriko_face_s5977_00001_.png"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\02_18歳_回想_新入社員"
os.makedirs(OUT, exist_ok=True)

# Upload reference image
print("Uploading reference image...")
with open(REF, "rb") as f:
    r = requests.post(f"{BASE}/upload/image", files={"image": ("yuriko_ref_18.png", f, "image/png")}, timeout=30)
print(f"Upload: {r.status_code} {r.json()}")

# Build workflow
wf = {
    "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "yayoi_mix.safetensors"}},
    "2": {"class_type": "LoraLoader", "inputs": {"model": ["1",0], "clip":["1",1], "lora_name":"JapaneseDollLikeness_v15.safetensors", "strength_model":0.5, "strength_clip":0.5}},
    "3": {"class_type": "LoraLoader", "inputs": {"model": ["2",0], "clip":["2",1], "lora_name":"DetailTweaker.safetensors", "strength_model":0.2, "strength_clip":0.2}},
    "4": {"class_type": "IPAdapterUnifiedLoaderFaceID", "inputs": {"model":["3",0], "preset":"FACEID PLUS V2", "lora_strength":0.5, "provider":"CPU"}},
    "5": {"class_type": "LoadImage", "inputs": {"image": "yuriko_ref_18.png"}},
    "6": {"class_type": "IPAdapterInsightFaceLoader", "inputs": {"provider":"CPU", "model_name":"buffalo_l"}},
    "7": {"class_type": "IPAdapterFaceID", "inputs": {"model":["4",0], "ipadapter":["4",1], "image":["5",0], "weight":0.8, "weight_faceidv2":0.0, "weight_type":"linear", "combine_embeds":"concat", "start_at":0.0, "end_at":1.0, "embeds_scaling":"V only", "insightface":["6",0]}},
    "8": {"class_type": "CLIPTextEncode", "inputs": {"text": "EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), cartoon, anime, illustration, makeup, long hair, hair past ears, curly hair", "clip":["3",1]}},
    "9": {"class_type": "CLIPTextEncode", "inputs": {"text": "(masterpiece, best quality:1.2), 8k, RAW photo, (Realistic, hyper realistic, photorealistic:1.3), ultra detailed, japanese young woman, 18 years old, petite small frame, plain natural face, short black bob haircut, hair ends at jawline, navy blazer with gold buttons, white blouse, knee-length navy skirt, uniform, front view, standing, looking at camera", "clip":["3",1]}},
    "10": {"class_type": "EmptyLatentImage", "inputs": {"width":512,"height":768,"batch_size":1}},
    "11": {"class_type": "KSampler", "inputs": {"seed":12345,"steps":28,"cfg":7.0,"sampler_name":"dpmpp_2m","scheduler":"karras","denoise":1.0,"model":["7",0], "positive":["9",0], "negative":["8",0], "latent_image":["10",0]}},
    "12": {"class_type": "VAEDecode", "inputs": {"samples":["11",0], "vae":["1",2]}},
    "13": {"class_type": "SaveImage", "inputs": {"filename_prefix":"test_ipadapter", "images":["12",0]}},
}

r = requests.post(f"{BASE}/prompt", json={"prompt":wf})
print(f"Submit: {r.status_code}")
if r.status_code == 200:
    pid = r.json()["prompt_id"]
    print(f"ID: {pid}")
    for j in range(120):
        time.sleep(2)
        h = requests.get(f"{BASE}/history/{pid}", timeout=10).json()
        if pid in h:
            st = h[pid]["status"]["status_str"]
            if st == "success":
                print("SUCCESS")
                for nid, node in h[pid]["outputs"].items():
                    for img in node.get("images",[]):
                        url = f"{BASE}/view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
                        out = os.path.join(OUT, img["filename"])
                        urllib.request.urlretrieve(url, out)
                        print(f"  Saved: {img['filename']} ({os.path.getsize(out)//1024}kb)")
                break
            elif st == "error":
                msg = h[pid]["status"]["messages"][-1][1].get("exception_message", "unknown")
                print(f"ERROR: {msg}")
                break
else:
    print(f"ERR: {r.text[:500]}")
