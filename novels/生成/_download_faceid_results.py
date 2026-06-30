"""
ComfyUI outputから生成画像を一括ダウンロード (UTF-8対応版)
"""
import requests, json, urllib.parse, os, io

BASE = "http://100.112.59.35:18188"
OUT = r"C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\橘百合子\02_18歳_回想_新入社員"
os.makedirs(OUT, exist_ok=True)

r = requests.get(f"{BASE}/history", timeout=30)
history = r.json()

downloaded = 0
for pid, data in history.items():
    if data["status"]["status_str"] == "success":
        for nid, node in data["outputs"].items():
            for img in node.get("images", []):
                fname = img["filename"]
                if not fname.startswith("百合子_18歳_yayoi_mix_s"):
                    continue
                outpath = os.path.join(OUT, fname)
                if os.path.exists(outpath):
                    continue
                params = urllib.parse.urlencode({"filename": fname, "subfolder": img["subfolder"], "type": img["type"]})
                url = f"{BASE}/view?{params}"
                try:
                    resp = requests.get(url, timeout=60)
                    if resp.status_code == 200:
                        with open(outpath, "wb") as f:
                            f.write(resp.content)
                        sz = len(resp.content) // 1024
                        print(f"  DL {fname} ({sz}kb)")
                        downloaded += 1
                    else:
                        print(f"  HTTP {resp.status_code} for {fname}")
                except Exception as e:
                    print(f"  FAIL {fname}: {e}")

print(f"Total downloaded: {downloaded}")
