# -*- coding: utf-8 -*-
import os, shutil

# Clear other images
basedir = r'C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラ画像\叔母\01_60代_札幌'
keep = 'oba_majic_v4_cfg8.0_s876174573_03_00001_.png'
bot = os.path.join(basedir, 'ボツ')
os.makedirs(bot, exist_ok=True)
for f in os.listdir(basedir):
    if f.endswith('.png') and f != keep:
        src = os.path.join(basedir, f)
        dst = os.path.join(bot, f)
        if os.path.exists(dst):
            os.remove(src)
        else:
            shutil.move(src, bot)
print('Files cleaned')

# Update setting file
md_path = r'C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラクター\叔母_誠の母方の叔母.md'
with open(md_path, 'r', encoding='utf-8') as f:
    content = f.read()

old = '## 画像生成情報\n- （モデル選定は後回し。yayoi_mixが高齢者表現に不向きなため、別モデルを検討）'
new = """## 画像生成情報

### 基本パラメータ
- ベースモデル: majicMIX.safetensors (SD1.5)
- LoRA: なし（majicMIXは不要）
- 解像度: 512x768 / Steps: 30 / CFG: 8.0 / Sampler: dpmpp_2m / Scheduler: karras
- CLIP skip: 2

### Negative Prompt
```
(worst quality:1.4), (low quality:1.4), (normal quality:1.2), EasyNegative, badhandv4, cartoon, anime, illustration, painting, 3d render, cgi, nude, exposed, oversaturated, hdr, airbrushed, plastic skin, mutated hands, mutated fingers, extra hands, extra arms, extra limbs, bad hands, bad fingers, missing fingers, missing hands, deformed hands, deformed fingers, multiple arms, multiple hands, watermark, signature, text, logo, young, girl, teen, 20s, 30s, 40s, heavy makeup, lipstick, eyeshadow, blush, kimono, decrepit, senile, dying, extreme aged, horror, ghost, haunted, dark, spooky
```

### バリアント一覧

| バリアント | フォルダ | 手法 |
|-----------|---------|------|
| 札幌・叔母（60代） | 01_60代_札幌/ | majicMIX（部長と同一パラメータ） |

- 採用画像: `oba_majic_v4_cfg8.0_s876174573_03_00001_.png`"""

content = content.replace(old, new)
with open(md_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Setting file updated')
