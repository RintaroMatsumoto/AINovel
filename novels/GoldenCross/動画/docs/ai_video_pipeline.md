# 無料 AI 動画生成パイプライン

AI-Influencer プロジェクトで確立した「完全無料 AI 動画生成」のノウハウ。
2台のローカルGPU (M1/M2) をOSSツールで使い倒す。

---

## 無料 vs 有料 対比

ずんブロ！(the-time.jp) の有料スタック (月$500-800相当) を完全無料で再現:

| 有料ツール | 月額 | 無料代替 | マシン |
|-----------|------|---------|-------|
| Conoha AI Canvas | 1,100円〜 | ComfyUI ローカル | M1/M2 |
| HeyGen ($29/mo) | ~4,500円 | LivePortrait + SadTalker | M2 |
| Runway ($12/mo) | ~1,800円 | LTX-Video + AnimateDiff + Wan 2.1 | M1/M2 |
| Magnific Premium+ | 4,875円 | Flux GGUF + SDXL ローカル | M1/M2 |
| **合計** | **~$500-800** | **$0** | — |

---

## パイプライン全体像

```
                     FREE PIPELINE

  台本 ──→ VOICEVOX ──→ WAV ──┐
  (TXT)    (無料TTS)          │
                              ├──→ Lip-Sync ──→ MP4 ──→ SNS
  顔画像 ──→ 前処理 ──→ PNG ──┘    (LivePortrait/
  (SDXL)                           SadTalker)

  画像生成: Prompt ──→ SDXL/Flux ──→ PNG ──→ Upscale ──→ 投稿
                              (Real-ESRGAN)

  動画生成: PNG ──→ Wan 2.2/LTX-Video ──→ MP4 ──→ Upscale ──→ SNS
```

---

## マシン別パイプライン

### 静止画投稿
```
[1] プロンプト生成 (Claude) → prompt.txt
[2] 画像生成 (M2, ~4秒/枚) → 50-100枚
[3] 品質選別 (顔一貫性 > 0.65)
[4] Upscale (M2, Real-ESRGAN)
[5] 後処理 (作業端末)
```

### リップシンク動画
```
[1] 台本生成 (Claude) → script.txt
[2] 音声合成 (VOICEVOX 無料) → script.wav
[3] 顔画像生成 (M2, SDXL)
[4] リップシンク (M2, LivePortrait) → talking.mp4
[5] Upscale (M2, Real-ESRGAN per-frame)
[6] 字幕 + AI開示 (FFmpeg)
[7] 投稿 (YouTube Shorts / TikTok)
```

### Wan 高品質動画
```
[1] 参照画像 (M2 SDXL) → portrait.png
[2] プロンプト生成 (Claude)
[3] Wan 動画生成 (M1 or M2, 832x480 5-10秒)
[4] Upscale + フレーム補間 (M2)
[5] BGM追加 (FFmpeg) → 完成
```

---

## 主力モデル一覧

| モデル | 用途 | 商用利用 |
|--------|------|:-------:|
| RealVisXL_V5.0 | 実写系画像 | ✅ |
| IllustriousXL_v01 | アニメ/NSFW | ✅ |
| ponyDiffusionV6 | アニメ | ✅ |
| flux1-schnell GGUF | 高品質画像 | Apache 2.0 ✅ |
| Wan 2.2 TI2V 5B | 画像→動画 | 標準 ✅ |
| Wan 2.1 T2V 1.3B | テキスト→動画 | 標準 ✅ |
| LTX-Video 2B | 高速動画 | ✅ |
| LivePortrait | リップシンク | Apache 2.0 ✅ |
| Real-ESRGAN | 高解像度化 | ✅ |

---

## Wan 2.2 動画生成 推奨パラメータ

| パラメータ | 値 |
|-----------|-----|
| 解像度 | 832×480 または 512×512 |
| フレーム数 | 16〜81fr (~5秒) |
| Steps | 20 |
| CFG | 6.0 |
| Scheduler | beta |
| Sampler | euler |
| CLIP | `umt5_xxl` (Wan用) |
| VAE | `wan_2.1_vae` (Wan2.2でも互性) |
| Attention | sageattn推奨 |

### VRAM消費目安 (M2 Wan 2.1)

| 解像度 | フレーム数 | VRAM |
|--------|-----------|:----:|
| 512×288 | 49fr | 2.9GB |
| 640×368 | 81fr | 6.4GB |
| 832×480 | 81fr | 8.2GB |
| 832×480 | 160fr (10秒) | 8.3GB |

---

## 商用利用ライセンス 早見

| モデル | ライセンス | 商用OK? |
|--------|-----------|:------:|
| FLUX.1-schnell | Apache 2.0 | ✅ |
| FLUX.1-dev/fill | 非商用 | ⚠️ 要確認 |
| Wan 2.1/2.2 | 標準 | ✅ |
| LivePortrait | Apache 2.0 | ✅ (要個別確認) |
| Real-ESRGAN | BSD 3-Clause | ✅ |
| VOICEVOX | 商用可(要クレジット) | ✅ |
