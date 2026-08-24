# リモートマシン構成 (M1 / M2)

AI-Influencer プロジェクトから継承。2台の Windows GPU マシンを SSH + Docker で遠隔操作する体制。

---

## マシンスペック

| 項目 | M1 | M2 |
|------|:-------------:|:-------------:|
| GPU | RTX 3060 **12GB** | RTX 3080 **10GB** |
| 画像生成速度 | ~12秒/枚 | **~4秒/枚 (3倍速)** |
| ロール | 動画生成主機 + LoRA訓練 | 高速画像 + リップシンク |
| ComfyUI Image | `ghcr.io/ai-dock/comfyui:m1-stable` (70GB) | `ghcr.io/ai-dock/comfyui:custom` (15GB) |
| ComfyUI port | **18188** | **18188** |
| PyTorch | 2.5.1+cu124 | 2.5.1+cu124 |
| SageAttention | 1.0.6 有効 | 1.0.6 有効 |
| Docker Desktop | 4.77.0 | 4.77.0 |

## 接続情報

| 項目 | M1 | M2 |
|------|----|----|
| **IP** | `100.112.59.35` | `100.107.17.85` |
| **SSH** | `admin` / `admin` | `admin` / `admin` |
| **ComfyUI API** | `http://100.112.59.35:18188` | `http://100.107.17.85:18188` |
| **Docker** | `docker exec comfyui` | `docker exec comfyui` |

### SSH 接続 (Python paramiko)
```python
import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('100.112.59.35', username='admin', password='admin')
```

### Docker exec 経由コマンド
```python
stdin, stdout, stderr = ssh.exec_command('docker exec comfyui nvidia-smi')
print(stdout.read().decode())
```

### ComfyUI 内部 Python (venv注意)
```python
# 正: venvのpipを使う
ssh.exec_command('docker exec comfyui /opt/environments/python/comfyui/bin/pip install <package>')

# 誤: システムPythonに入ってしまう
ssh.exec_command('docker exec comfyui pip install <package>')
```

---

## マシン分担ルール

| ワークロード | 担当 | 理由 |
|-------------|------|------|
| **画像生成 (SDXL/Flux)** | M2優先 | 3倍高速 |
| **Wan 2.2 動画 (I2V 5B)** | M1 (または両機) | M1モデル完備 |
| **Wan 2.1 動画 (T2V 1.3B)** | M2 | M2モデル完備 |
| **LTX-Video 2B 動画** | M1のみ | モデルがM1のみ |
| **LoRA訓練 (SDXL)** | 両機可能 | M1はbatch大、M2はbatch=1 |
| **Flux LoRA訓練** | M1のみ | 12GB必要 |
| **リップシンク (LivePortrait)** | M2 | ノード完備 |
| **LLM推論 (Ollama)** | M2推奨 | M1はキュー詰まり多発 |

---

## ComfyUI 起動オプション

```bash
# 両機共通
--lowvram --force-fp16

# M2 追加推奨
--dont-upcast-attention

# SageAttention 有効化（両機）
--use-sage-attention
```

---

## 既知の制約

- **ポート番号**: ComfyUI は port **18188** で稼働（8188 ではない）
- **M2 SSH 障害履歴**: sshd サービス登録が欠損することがある。復旧:
  ```
  sc.exe create sshd binpath="C:\Windows\System32\OpenSSH\sshd.exe"
  ```
- **M2 Docker Desktop**: SSH切断時に停止する。再接続時は手動起動が必要。
- **ComfyUI 再起動**: クラッシュ時は以下で復旧:
  ```
  docker compose down comfyui && docker compose up -d comfyui
  ```

---

## NAS 連携 (Buffalo LinkStation)

| 項目 | 値 |
|------|-----|
| NAS IP | `192.168.1.2` |
| 共有パス | `\\192.168.1.2\share\ai_collab` |
| 認証 | admin / admin |
| 本機マウント | Z: ドライブ |

用途別:
- LoRAモデル: `lora/<persona_id>/`
- 生成画像: `assets/generated_images/<YYYY-MM>/`
- 動画素材: `assets/videos/<project_id>/`
- データセット: `datasets/<job_id>/`
