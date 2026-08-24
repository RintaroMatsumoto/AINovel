# ComfyUI API 実戦リファレンス

AI-Influencer プロジェクトで確立した ComfyUI 遠隔操作ノウハウ。

---

## 主要 HTTP エンドポイント

| メソッド | パス | 用途 |
|---------|------|------|
| POST | `/prompt` | workflow JSON 投入、`prompt_id` 取得 |
| GET | `/history/{prompt_id}` | 完了確認・結果取得 |
| GET | `/view?filename=...&subfolder=...&type=output` | 生成画像/動画 download |
| GET | `/queue` | キュー状態 (running / pending) |
| GET | `/system_stats` | 起動確認・GPU状態 |
| POST | `/interrupt` | 実行中ジョブ中断 |
| POST | `/upload/image` | 画像 upload (multipart/form-data) |
| WS | `/ws` | 進捗 WebSocket |
| GET | `/object_info/{node_type}` | ノードの入力情報取得 (checkpoint一覧等) |

---

## PowerShell からの基本投入テンプレート

```powershell
# === 変数 ===
$IP = "100.107.17.85:18188"                # M2 (M1は 100.112.59.35)
$CKPT = "IllustriousXL_v01.safetensors"     # マシンに合わせる
$PROMPT = "masterpiece, best quality, 1girl, ..."
$OUTDIR = "C:\Users\GoldRush\Desktop\Test"

# === Workflow JSON ===
$wf = @{
  "4" = @{ class_type = "CheckpointLoaderSimple"; inputs = @{ ckpt_name = $CKPT } }
  "5" = @{ class_type = "EmptyLatentImage"; inputs = @{ width = 832; height = 1216; batch_size = 1 } }
  "6" = @{ class_type = "CLIPTextEncode"; inputs = @{ text = $PROMPT; clip = @("4", 1) } }
  "7" = @{ class_type = "CLIPTextEncode"; inputs = @{ text = $NEGATIVE; clip = @("4", 1) } }
  "3" = @{ class_type = "KSampler"; inputs = @{ seed = 42; steps = 25; cfg = 6.0; sampler_name = "euler"; scheduler = "normal"; denoise = 1.0; model = @("4", 0); positive = @("6", 0); negative = @("7", 0); latent_image = @("5", 0) } }
  "8" = @{ class_type = "VAEDecode"; inputs = @{ samples = @("3", 0); vae = @("4", 2) } }
  "9" = @{ class_type = "SaveImage"; inputs = @{ filename_prefix = "output"; images = @("8", 0) } }
}

# === Submit (重要な注意点) ===
# $pId は使わない！PowerShell予約語 $PID と衝突する
$body = @{prompt=$wf} | ConvertTo-Json -Depth 10
$res = Invoke-WebRequest -Uri "http://$IP/prompt" `
    -Method POST -Body $body -ContentType "application/json" `
    -UseBasicParsing -TimeoutSec 15
$promptKey = ($res.Content | ConvertFrom-Json).prompt_id
```

---

## Python からの基本投入テンプレート

```python
import requests, json, time

BASE = "http://100.107.17.85:18188"  # M2

wf = json.load(open("workflows/target_workflow.json"))
wf["3"]["inputs"]["seed"] = 12345
wf["6"]["inputs"]["text"] = "masterpiece, 1girl, ..."

pid = requests.post(f"{BASE}/prompt", json={"prompt": wf}).json()["prompt_id"]

while True:
    h = requests.get(f"{BASE}/history/{pid}").json()
    if pid in h:
        break
    time.sleep(2)

outputs = h[pid]["outputs"]
for nid in outputs:
    for img in outputs[nid].get("images", []):
        url = f"{BASE}/view?filename={img['filename']}&subfolder={img.get('subfolder','')}&type={img['type']}"
        resp = requests.get(url)
        with open(img["filename"], "wb") as f:
            f.write(resp.content)
```

---

## Workflow JSON の2つの形式

| 形式 | 保存方法 | APIで使える？ |
|------|---------|:---:|
| **UI Format** | 普通の Save | ❌ |
| **API Format** | Settings → Dev mode Options → Enable → Save (API Format) | ✅ |

`workflows/*.json` は **必ず API Format** で保存すること。

---

## トラブルシューティング

| 症状 | 原因・対処 |
|------|-----------|
| `--listen` なしで起動して外部接続不可 | 必ず `--listen 127.0.0.1` or `0.0.0.0` を付ける |
| GPU OOM | batch_size=1、解像度1024以下、`--lowvram` flag |
| ワークフローが動かない | custom_nodes が未install。Manager API で install する |
| M2 で人物が生成されない | `wai-nsfw-illustrious-v17` は人物生成不可。`IllustriousXL_v01` を使う |
| Illustrious系で人物が出ない | Danbooru タグ形式を使う（自然言語不可） |
| M2 ネガティブプロンプト | 30トークン以内に抑える。超えるとエラー |
| ComfyUI 起動が遅い | `/system_stats` が 200 を返すまで polling する |

### モデル系統とプロンプト形式

| モデル系統 | プロンプト形式 | 例 |
|-----------|--------------|-----|
| SDXL 実写系 (RealVis, Juggernaut) | 自然言語 | `a Japanese woman standing in neon city` |
| Illustrious/WAI/NoobAI 系 | Danbooru タグ | `1girl, black hair, purple eyes, standing` |
| Pony Diffusion 系 | Danbooru タグ + rating | `score_9, score_8_up, 1girl, ...` |

---

## マシン別 checkpoint 一覧

| M1 (100.112.59.35) | M2 (100.107.17.85) |
|---|---|
| `IllustriousXL_v01.safetensors` | `Juggernaut-XL_v9.safetensors` |
| `JuggernautXL_v9.safetensors` | `RealVisXL_V5.0_fp16.safetensors` |
| `RealVisXL_V5.0_fp16.safetensors` | `ponyDiffusionV6XL.safetensors` |
| `ltx-video-2b-v0.9.8-distilled-fp8.safetensors` | `wai-nsfw-illustrious-v17.safetensors` (人物非互換) |
| `ponyDiffusionV6.safetensors` | — |
| `sd_xl_base_1.0.safetensors` | — |

### Wan 動画生成モデル

| モデル | M1 | M2 |
|--------|:--:|:--:|
| Wan 2.2 TI2V 5B (I2V, fp16/GGUF) | ✅ | — |
| Wan 2.1 T2V 1.3B | — | ✅ |
| LTX-Video 2B v0.9.8 fp8 | ✅ | — |
| AnimateDiff Lightning | ✅ | ✅ |

### Wan 動画生成用 CLIP

| CLIP | M1 | M2 |
|------|:--:|:--:|
| `umt5_xxl_fp8_e4m3fn_scaled.safetensors` | — | ✅ (Wan用) |
| `t5xxl_fp8_e4m3fn.safetensors` | ✅ | ✅ (Flux用) |
