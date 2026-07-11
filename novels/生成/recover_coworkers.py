# Recovery script for coworker images from M1
import requests, urllib.parse, os

BASE = 'http://100.112.59.35:18188'
BASE_OUT = r'C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像'

r = requests.get(BASE+'/history')
h = r.json()

targets = {
    'ito': ('伊藤\\01_35歳_経理課', []),
    'inoue': ('井上\\01_28歳_経理課', []),
    'kinoshita': ('木下\\01_30代_経理課', []),
}

for pid, data in h.items():
    for nid, node in data.get('outputs',{}).items():
        for img in node.get('images',[]):
            for tag, (folder, _) in targets.items():
                if f'{tag}_majic' in img['filename']:
                    targets[tag][1].append(img)
                    break

for tag, (folder, images) in targets.items():
    out_dir = os.path.join(BASE_OUT, folder)
    os.makedirs(out_dir, exist_ok=True)
    for img in images:
        params = urllib.parse.urlencode({'filename': img['filename'], 'subfolder': img['subfolder'], 'type': img['type']})
        url = f'{BASE}/view?{params}'
        resp = requests.get(url, timeout=60)
        if len(resp.content) > 1000:
            path = os.path.join(out_dir, img['filename'])
            with open(path, 'wb') as f: f.write(resp.content)
            print(f'OK {tag}: {img["filename"]} ({len(resp.content)//1024}kb)')
