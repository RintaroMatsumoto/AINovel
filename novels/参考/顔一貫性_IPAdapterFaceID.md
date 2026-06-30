# IPAdapterFaceID 顔一貫性生成 技術ノウハウ

## 1. Purpose

IPAdapterFaceID を使う理由：seed固定だけではプロンプト変化（服装・構図の違い）で顔が変わるため。

解決方法：参照画像から顔ベクトルを抽出し生成過程に注入、顔構造を維持したまま服装/髪型/構図だけを書き換える。

## 2. Architecture

- InsightFace (buffalo_l): 顔の特徴点抽出・ベクトル化
- CLIP Vision (ViT-H): 画像全体のスタイル・文脈理解
- FaceID Plus V2: 顔ベクトル+CLIP特徴を生成過程に注入

## 3. Recommended Parameters (SD1.5, verified)

- プリセット: FACEID PLUS V2
- weight: 0.8 (range 0.7-0.9)
- weight_faceidv2: 0.0 (not for SD1.5)
- weight_type: linear
- embeds_scaling: V only (face structure only, no style)
- provider: CPU (InsightFace, GPU unstable)
- LoRA strength: 0.5 (auto-loaded by preset)

## 4. Required Models (SD1.5)

- ip-adapter-faceid-plusv2_sd15.bin → models/ipadapter/ (150MB)
- ip-adapter-faceid-plusv2_sd15_lora.safetensors → models/loras/ (49MB)
- CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors → models/clip_vision/ (2.4GB)
- Note: filename matching is strict regex in Cubiq's utils.py

## 5. Preset to Filename Mapping (from Cubiq ComfyUI_IPAdapter_plus utils.py)

- FACEID → faceid.sd15.bin
- FACEID PLUS — SD1.5 only → faceid.plus.sd15.bin (v1, deprecated)
- FACEID PLUS V2 → faceid.plusv2.sd15.bin (CURRENTLY USED)

## 6. Performance Notes

- First image: ~5 min on M1 (RTX3060) — loads CLIP Vision + InsightFace models
- Subsequent: ~2 min per image
- Recommend 300+ second timeout in scripts

## 7. File Naming Rule

- ASCII ONLY (Japanese chars corrupt via ComfyUI API download)
- Pattern: {char_en}_{age}_{model}_s{seed}_{clothes}_{hair}_{angle}_{seq}.png
- Example: yuriko_18_yayoi_mix_s9964889205_uniform_bob_front_00001_.png

## 8. Project Scripts

- novels/生成/gen_yuriko_faceid.py — 12-variant batch generation
- novels/生成/_test_ipadapter.py — single image test
- novels/生成/_scp_faceid_results.py — SSH copy from Docker (avoids API encoding issues)

## 9. Connection Info

- M1: 100.112.59.35:18188, SSH admin/admin, Docker comfyui
- Model: yayoi_mix.safetensors (SD1.5)
- LoRAs: JapaneseDollLikeness_v15 (0.5) + DetailTweaker (0.2)
- Resolution: 512×768, Steps 28, CFG 7.0, Sampler dpmpp_2m, Scheduler karras
- Reference image: yuriko_face_s5977_00001_.png (seed 5977 confirmed as Yuriko 18yo face)

## 10. Prior Research Found Parameters

- weight 0.8 > 0.7 (stronger face preservation)
- embeds_scaling V only > V+style or None (doesn't inject style)
- linear > ease-in-out (slightly more consistent)
- buffalo_l > antelopev2 (better FaceID compatibility with SD1.5)
- No noise/stop_at options needed for FaceID (only for regular IPAdapter)

## 11. Age Progression Technique (from 34yo Yuriko experiments)

### Problem
SD1.5 + yayoi_mix strongly biases toward young beautiful faces. FaceID from 18yo reference preserves young facial structure. Previously tried skin degradation keywords (wrinkles/sagging) → image quality loss.

### Solution: Eye-Focused Aging (2025-06-29 experiment)

| Finding | Detail |
|---------|--------|
| **FaceID weight reduction** | 0.8→0.3 lets prompt aging take priority over face preservation |
| **JapaneseDollLikeness removal** | 0.5→0.0 prevents beautification smoothing |
| **CFG increase** | 7.0→10.0 strengthens prompt adherence for age keywords |
| **Texture keywords FAIL** | `wrinkles, sagging, rough skin, hollow cheeks` → degraded image quality |
| **Eye/expression keywords WIN** | `tired heavy-lidded eyes, exhausted distant gaze, weary expression` → natural aging without degradation |

### Proven Prompt Structure (PB / Yuriko 34yo)
```
Pos prefix:
(masterpiece, best quality:1.2), 8k, RAW photo,
(Realistic, hyper realistic, photorealistic:1.3), ultra detailed,
34-years-old, mature woman, thirties,
long straight black hair, [hair_detail],
plain natural face, no makeup

Aging keywords:
mother of two, experienced tired gaze,
distant thoughtful expression, quiet weariness,
natural aging around eyes, subdued expression

Negative additions for age:
young, teen, adolescent, childish,
cute, kawaii, innocent,
glowing skin, radiant, fresh-faced
```

### Key Insight
Don't try to make the face "look old" (wrinkles, texture). Instead make the face "look tired" (eyes, expression, posture). A 34yo mother of two with 16 years of secret trauma shows her age through her **eyes and demeanor**, not her skin.

### Confirmed Parameter Sets

| Age | Doll | DetailTweaker | FaceID | CFG | Prompt Style |
|-----|------|--------------|--------|-----|-------------|
| 18yo | 0.5 | 0.2 | 0.8 | 7.0 | Default face preservation |
| 20yo | 0.0 | 0.2 | 0.8 | 8.0 | +Dual IPAdapter for hair |
| 34yo | 0.0 | 0.2 | 0.3 | 10.0 | PB: eye-focused aging |

## 12. Dual IPAdapter Workflow (20yo Yuriko)

For hair consistency across ages, use two IPAdapters in series:
1. **FaceID** (weight 0.8): Facial identity preservation
2. **Regular IPAdapter STANDARD** (weight 0.25): Hair style transfer from a reference image

Requires `ip-adapter_sd15.safetensors` (43MB) in models/ipadapter/.
Dual IPAdapter nodes chain: FaceID output → Regular IPAdapter input.

## 13. Character Generation Pipeline (for reuse)

When generating a NEW character from scratch:

### Phase 1: Reference Face
1. Generate 1 seed-only image without FaceID → check face quality
2. Optionally use seed that gives best face as FaceID reference
3. Upload reference to ComfyUI

### Phase 2: Test FaceID
4. Generate 1-3 test images with FaceID (weight 0.8) → confirm face consistency
5. Save test results in `{char_name}/テスト/`

### Phase 3: Age-Specific Generation
6. For young age (<20): FaceID 0.8, CFG 7.0, Doll 0.5
7. For middle age (~34): FaceID 0.3, CFG 10.0, Doll 0.0, PB prompts
8. For aged/weathered: FaceID 0.2, CFG 10-12, Doll 0.0, DT 0.0

### Phase 4: Organization
9. Move final picks to `採用/`, rest to `ボツ/`
10. Update `novels/設定/キャラクター/{name}.md` with exact params and seed list

## 14. File Organization Standard

```
{age}_{context}/
├── 採用/  ← final selected images
├── ボツ/  ← rejected/generation attempts
└── (optional) single/ ← old pipeline variants
```

Adopted images should have filename pattern:
`{char}_{age}_{model}_s{seed}_{variant}_00001_.png`

## 15. 橘誠 24歳 — FaceID 実績

### 決定パラメータ
- 参照顔: `makoto_24_yayoi_mix_s1193774_sidepart_a4_00001_.png` (seed 1193774、会議室カット)
- 参照顔復元: seed=1193774、M1履歴から完全再現可能（`/history` API → prompt_id検索）
- 髪型: 七三分け・ナチュラル（保守的サラリーマン、ホスト感排除）
- FaceID weight: 0.8 (fid8)
- LoRA: DetailTweaker 0.2のみ（JapaneseDollLikeness不使用）
- CFG: 7.0（標準）

### 男性顔の注意点
- **JapaneseDollLikeness禁止**: 女性用LoRA、男性に使用すると女顔になる
- **negativeにfeminine必須**: `feminine, woman, androgynous, soft face, delicate, pretty, girly`
- **ホスト髪防止**: pompadour, quiff, gel hair, excessive volume, undercutをnegative
- **生成モデルyayoi_mixが美顔寄り**：jawline強調、sharp features追加で対応

### 今後の年齢別戦略（予定）
| 年齢 | FaceID | IPAdapter | LoRA | CFG | 加齢表現 |
|------|--------|-----------|------|-----|---------|
| 24歳 | 0.8 | — | DetailTweaker 0.2 | 7.0 | — |
| 29歳（葬儀） | 0.6〜0.7 | — | DetailTweaker 0.2 | 7.0 | やや疲れ、スーツ |
| 40歳（現役） | **不使用** | STANDARD 0.45 standard | なし | 7.5 | 白髪混じり・目/表情 |
| 40歳（崩壊後） | 不使用 | STANDARD 0.45 standard | なし | 7.5 | 隈・窪み・乱れ |

## 16. IPAdapter Only Workflow (2026-07-01 discovery)

参照画像が**完成形（顔＋髪＋メガネ＋雰囲気）** の場合、FaceIDは不要。

### なぜか
- FaceID（InsightFace）は顔ベクトルのみ抽出 → 髪型・メガネ・表情は素通し
- Regular IPAdapter（CLIP Vision）は画像全体の埋め込みを抽出 → 顔＋髪＋全スタイルを一度に転送
- 両者を同時に使うと、異なる特徴空間からの情報が競合して一貫性を損ねる

### 使い分け

| 状況 | 使うもの | 理由 |
|------|---------|------|
| 若い参照から老化させる | FaceID 0.3 + CFG 10.0 | 百合子34歳。低FaceIDが老化を許容、高CFGが老化promptを強制 |
| 髪型だけ別参照から転送 | FaceID + IPAdapter Dual | 百合子20歳。顔はFaceID、髪はIPAdapterと役割分担 |
| **完成形の1枚を別シーンに転送** | **IPAdapterのみ** | **誠40歳。cafe_street1枚で顔＋髪＋メガネが完結 → FaceID不要** |

### 決定パラメータ（誠40歳 現役・実績）
- 参照: `cafe_street` (seed 6250727949、すでに40歳 × 銀縁メガネ × 白髪混じりの完成形)
- IPAdapter STANDARD ("medium strength"), weight **0.45**, weight_type **"standard"**
- CFG 7.5
- FaceID: **不使用**
- LoRA: 不使用（DetailTweakerは肌平滑化が老化と逆効果）
- 老化キーワード: 目・表情のみ（`tired eyes, weary gaze, dark circles, subdued expression`）
- 解像度/Steps/Sampler: 512×768 / 28 / dpmpp_2m karras

### 注意点
- weight 0.35 + "prompt is more important" では、参照と大きく異なる角度（正面→横顔など）で顔の同一性が落ちる
- **"standard"** + weight 0.45 が角度耐性の最適バランス
- CFG 7.5を超えるとprompt優位になりすぎて顔が変わる
