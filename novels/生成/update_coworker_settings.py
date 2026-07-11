# -*- coding: utf-8 -*-
import os

base = r'C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラクター'

SECTION = """

## 画像生成情報

### 基本パラメータ
- ベースモデル: majicMIX.safetensors (SD1.5)
- CLIP skip: 2 / Steps: 30 / CFG: 8.0 / Sampler: dpmpp_2m / Scheduler: karras
- 解像度: 512x768

### Negative Prompt
```
(worst quality:1.4), (low quality:1.4), EasyNegative, badhandv4, cartoon, anime, illustration, painting, 3d render, cgi, mutated hands, extra hands, bad hands, deformed hands, fashionable, stylish, trendy, elegant, model, handsome, beautiful, pretty, cute, attractive, makeup, lipstick, blush, young, smiling, happy
```
"""

IMAGES = {
    '伊藤_誠の部下（隣席）.md': '01_35歳_経理課/採用/ito_v2_cfg8.0_s817771457_01_00001_.png',
    '井上_誠の部下（若手）.md': '01_28歳_経理課/採用/inoue_v2_cfg8.0_s525982223_02_00001_.png',
    '木下_誠の部下.md': '01_30代_経理課/採用/kinoshita_v7_cfg8.0_s295309927_05_00001_.png',
}

for fname, img in IMAGES.items():
    path = os.path.join(base, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if '## 画像生成情報' in content:
        print(f'{fname}: already has 画像生成情報')
        continue
    content += SECTION
    content += f'### 採用画像\n- `{img}`\n'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'{fname}: updated')
