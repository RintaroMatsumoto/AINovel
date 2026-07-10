# -*- coding: utf-8 -*-
"""橘翼.md の画像生成情報をFaceID方式に更新"""
with open(r'C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラクター\橘翼.md', 'r', encoding='utf-8') as f:
    content = f.read()

new_section = """## 画像生成情報

### 基本パラメータ
- ベースモデル: yayoi_mix.safetensors (SD1.5)
- LoRA: DetailTweaker (0.2) — JapaneseDollLikeness不使用（男性のため）
- 解像度: 512×768 / Steps: 28 / CFG: 7.0 / Sampler: dpmpp_2m / Scheduler: karras

### 顔固定手法
- **手法**: IPAdapterFaceID PLUS V2（栞・百合子と同一手法）
- **参照画像**: `02_11歳_小学生/tsubasa_11_yurikos5977_07_00001_.png`（百合子seed 5977系。0歳はFaceID非使用）
- **InsightFace**: buffalo_l (CPU)
- **設定**: weight_faceidv2=0.0 / weight_type=linear / embeds_scaling=V only

### Negative Prompt（全バリアント共通）
```
EasyNegative, (worst quality:1.2), (low quality:2), (normal quality:2), cartoon, anime, illustration, painting, 3d render, cgi, nude, exposed, oversaturated, hdr, plastic skin, airbrushed, duplicate person, mutated hands, extra fingers, deformed, bad anatomy, watermark, signature, text, logo, existing celebrity, real person, copyrighted character, feminine, woman, female features, effeminate, androgynous, makeup, long hair, colored hair
```

### バリアント一覧

| 年齢 | フォルダ | FaceID weight | 手法 |
|:----:|---------|:-------------:|------|
| 0歳（乳児） | 01_0歳_乳児/ | 不使用 | seed 5977系（プロンプトのみ） |
| 11歳（小学生） | 02_11歳_小学生/ | 0.8 | FaceID + ランダムseed |
| 14歳（里親） | 03_14歳_里親/ | 0.75 | FaceID + ランダムseed |
| 14歳（少年院） | 04_14歳_少年院/ | 0.75 | FaceID + ランダムseed |
| 17歳（ホスト格闘家） | 05_17歳_ホスト格闘家/ | 0.8 | FaceID + ランダムseed |
| 20歳（タイトルマッチ） | 06_20歳_タイトルマッチ/ | 0.8 | FaceID + ランダムseed |
| 30歳（エピローグ） | 07_30歳_エピローグ/ | 0.8 | FaceID + ランダムseed |

- 各フォルダに `採用/`（選定済み）と `ボツ/`（候補落ち・旧画像）のサブフォルダを持つ
- 旧フォルダ（01_11歳_小学生/ 等）の画像は全て対応する新フォルダの `ボツ/` に集約済み
"""

marker = '## 画像生成情報'
idx = content.find(marker)
if idx >= 0:
    new_content = content[:idx] + new_section
    with open(r'C:\Users\GoldRush\Documents\MyProject\AINovel\novels\設定\キャラクター\橘翼.md', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print('OK: updated')
else:
    print('ERR: marker not found')
