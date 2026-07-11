# Recover kinoshita v3 images from M1
import requests, urllib.parse, os

BASE = 'http://100.112.59.35:18188'
OUT = r'C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\木下\01_30代_経理課'
os.makedirs(OUT, exist_ok=True)

r = requests.get(BASE+'/history')
h = r.json()
count = 0
for pid, data in h.items():
    for nid, node in data.get('outputs',{}).items():
        for img in node.get('images',[]):
            if 'kinoshita_v3' in img['filename']:
                params = urllib.parse.urlencode({'filename':img['filename'],'subfolder':img['subfolder'],'type':img['type']})
                resp = requests.get(f'{BASE}/view?{params}', timeout=60)
                if len(resp.content) > 1000:
                    path = os.path.join(OUT, img['filename'])
                    with open(path, 'wb') as f: f.write(resp.content)
                    print(f'OK: {img["filename"]} ({len(resp.content)//1024}kb)')
                    count += 1
print(f'{count} files recovered')
