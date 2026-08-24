# プロジェクト横断ノウハウ集

2026年7月時点。AINovel（小説執筆） + AIvideo（動画生成）の実戦知を集約。

---

## 1. 全体アーキテクチャ

```
小説執筆 (AINovel/)             音声合成                動画生成 (AIvideo/)
┌─────────────────┐     ┌──────────────────┐     ┌──────────────────────┐
│ opencode        │     │ VOICEVOX         │     │ ComfyUI (M1/M2)      │
│ custom agents   │──→  │ (localhost:50021) │──→ │ Wan / SDXL / LTX     │
│ story-long-write│     │ Python TTS script │     │ LivePortrait         │
│ narrative-writer│     │ WAV chunk merge   │     │ FFmpeg MCP server    │
└─────────────────┘     └──────────────────┘     └──────────────────────┘
```

### マシン構成
| マシン | GPU | IP | 役割 |
|-------|-----|----|------|
| M1 | RTX 3060 12GB | 100.112.59.35:18188 | Wan動画生成主機、LoRA訓練 |
| M2 | RTX 3080 10GB | 100.107.17.85:18188 | 高速画像生成、リップシンク |
| 本機 | (作業端末) | — | VOICEVOX TTS、コード編集 |

### 接続 (paramiko)
```python
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('100.112.59.35', username='admin', password='admin')
# Docker exec: ssh.exec_command('docker exec comfyui nvidia-smi')
```

---

## 2. AINovel — 小説執筆パイプライン

### 2.1 プロジェクト構造
```
novels/
├── 設定/          # キャラ・世界観（全集共通）
├── 参考/          # 調査・分析ファイル
├── 追跡/          # 伏線・時間線・文脈（全集共通）
├── GoldenCross/   # Vol.1 誠編（現在執筆中）
│   ├── プロット/  # 大綱
│   ├── 構成/      # 細綱（章ごと）
│   └── 本文/      # 本文.md + .wav
├── デッドクロス/  # Vol.2 栞編
└── ブレイクアウト/ # Vol.3 翼編
```

### 2.2 三部作構成
| 巻 | タイトル | 主人公 | あらすじ |
|----|---------|--------|---------|
| 1 | GoldenCross | 橘誠 (40歳) | 1億達成→封筒6通→精神破壊→心中 |
| 2 | DeadCross | 橘栞 (14→18歳) | 施設→立ちんぼ→トレード→金子殺害→死亡 |
| 3 | Breakout | 橘翼 (11→30歳) | 里親→少年院→格闘技→車椅子トレーダー→施設建設 |

### 2.3 核となる技法：滲み出し層 (Seepage Layer)
**百合子視点の独立した章を設けず**、誠の現在の内省から過去の百合子の意識へ自然に滲み出させる。
- 境界マーク（`***`等）を使わない
- 知覚（光の質・温度・身体感覚）の変化のみで過去へ滑り込む
- 封筒（L1〜L6）→ 誠の回想 → 滲み出し の三層構造

| 章 | 封筒 | 滲み出し | 内容 |
|----|:----:|:--------:|------|
| 2 | L1 | — | 教育係時代 |
| 3 | L2 | ①レイプ・警察 | 読者が初めて真実を知る |
| 4 | L3 | ②脅迫・動画支配 | 十二月の日付が嘘を暴く |
| 5 | L4 | ③交際中もレイプ継続 | デートの幸福が根本から汚染 |
| 6 | L5 | — | 家の記憶が写真で決定的に汚染 |
| 7 | 空白月 | ④托卵 | 生活費停止→自壊 |
| 8 | L6 | — | 告白→自死 |

### 2.4 7次元言語スタイル（キャラの声の違い）
| キャラ | 声質 | 参照作家 |
|--------|------|---------|
| 誠 | 理論派・数字で世界を把握。封筒ごとに文体が質的に変化 | 村上春樹 |
| 栞 | 二重言語（お嬢様言葉とストリート）。怒りの時が最も冷徹 | 金原ひとみ＋桐野夏生 |
| 翼 | 各フェーズで声が変わる。幼少期=怯え→最終的に誠の文体に近づく | 村上春樹 |

### 2.5 執筆ワークフロー（1章あたり）
1. **Step 0**: story-explorer spawn（参照ファイル探索＋前章末尾取得）
2. **Step 1**: narrative-writer spawn（初稿）
3. **Step 2a**: consistency-checker spawn（事実矛盾チェック）
4. **Step 2b**: chapter-extractor spawn（要約＋情節点抽出）※並列
5. **Step 3**: S1/S2がある場合のみnarrative-writer再spawn
6. **Step 4**: メインAI最終チェック（8工程）
7. **品質チェック**: 字数検証 / 章末チェック / 元情報スキャン / 標点正規化 / 禁用語スキャン / 感情目標達成度 / 追跡更新

### 2.6 設定変更管理
```
蓄積フェーズ（ユーザーが「反映して」と言うまで変更を積む）
  → 一括反映フェーズ（L1大綱→L2細綱→L3追跡→L4本文→L5品質）
```
- 変更ログは `追跡/設定変更ログ.md` で一元管理
- 同じ章を何度も修正すると文体一貫性が崩れるため、バッチ処理が鉄則

### 2.7 禁止事項（設計判断）
- 章タイトルは付けない（`## 第X章` 番号のみ）
- 境界マークでの回想区切り禁止
- 章末の総括・教訓・哲理禁止（余韻で閉じる）
- 取引手法の記述禁止
- 独立した百合子視点の章は設けない
- ノートは人形の背中にある（物理的には一切登場しない）
- ノートの具体的な文言は引用しない
- 設定にない具体的文言を創作しない

### 2.8 祖父のノート（最重要設定）
- 人形の背中に **金貨10枚・手紙・ノート** の3つが入っていた
- 手紙は祖父から誠への私信。ノートは投資の心構えを説く羅針盤
- 具体的な投資手法は一切書かれていない
- 三代継承：祖父→誠→栞→翼

---

## 3. VOICEVOX TTS — 音声合成

### 3.1 起動手順
```powershell
Start-Process "C:\Program Files\VOICEVOX\VOICEVOX.exe" -WindowStyle Hidden
Start-Sleep -Seconds 25
# Engine確認
& python -c "import urllib.request; req=urllib.request.Request('http://127.0.0.1:50021/version'); resp=urllib.request.urlopen(req,timeout=10); print('OK:', resp.read().decode())"
```

### 3.2 話者一覧
| 話者 | ID | 特徴 |
|------|:--:|------|
| 波音リツ | 9 | 落ち着いた低めの男声（初期設定） |
| 雀松朱司 | 52 | 大人の男性（現在使用中） |
| 玄野武宏 | 11 | やや若めの男性（感情別あり） |
| 白上虎太郎 | 12 | 少年っぽい男声 |
| 青山龍星 | 13 | 低めの大人の男声 |
| 四国めたん | 0/2 | 女性・様々なスタイル |
| ずんだもん | 1/3 | 可愛め女性声 |

### 3.3 TTSスクリプト (`voicevox_tts_v2.py`)
**主要パラメータ:**
| 項目 | 値 | 説明 |
|------|-----|------|
| BASE | `http://127.0.0.1:50021` | VOICEVOX API |
| SPEAKER | 52 | 話者ID |
| CHUNK_MAX_CHARS | 500 | 1回の合成上限文字数 |
| MAX_RETRIES | 3 | chunk失敗時のリトライ回数 |
| RETRY_DELAY | 3 | リトライ間隔(秒) |

**処理フロー:**
1. テキストを段落区切り → 500字以内のchunkに分割
2. `POST /audio_query?speaker={ID}&text={...}` → audio_query取得
3. `POST /synthesis?speaker={ID}` → WAVバイナリ取得
4. 全chunkをWAV結合（`wave`モジュールで連結）
5. 出力: 同名.wav

**実績:**
- 第1章_v3: 4,828文字 → 10chunk → 32.6MB → 3.0分（雀松朱司）
- 通信より合成がボトルネック（1chunkあたり15〜20秒）

**Tips:**
- エンジンが落ちたら `engine_alive()` が検出しリトライ
- chunk間に0.3秒のインターバル推奨（エンジン負荷軽減）
- 出力先は `OUTPUT_DIR` で指定
- 話者変更は `SPEAKER` 変数のみ変更すればOK

---

## 4. ComfyUI — 画像・動画生成

### 4.1 遠隔操作API
| エンドポイント | 用途 |
|--------------|------|
| `POST /prompt` | workflow投入、`prompt_id`取得 |
| `GET /history/{id}` | 完了確認・結果取得 |
| `GET /view?filename=...&subfolder=...&type=output` | 生成物ダウンロード |
| `GET /system_stats` | 起動確認・GPU状態 |

### 4.2 Workflow注意点
- UI Format（通常保存）はAPIから使えない
- **API Format**（Settings→Dev mode Options→Save API Format）で保存必須

### 4.3 プロンプトの形式
| モデル系統 | 形式 | 例 |
|-----------|------|-----|
| SDXL実写系 (RealVis/Juggernaut) | 自然言語 | `a Japanese woman standing in neon city` |
| Illustrious/WAI/NoobAI系 | Danbooruタグ | `1girl, black hair, purple eyes, standing` |
| Pony Diffusion系 | Danbooru + rating | `score_9, score_8_up, 1girl, ...` |

### 4.4 マシン別モデル
| M1 (100.112.59.35) | M2 (100.107.17.85) |
|---|---|
| IllustriousXL_v01 | Juggernaut-XL_v9 |
| ltx-video-2b-v0.9.8-fp8 | RealVisXL_V5.0 |
| Wan 2.2 TI2V 5B (I2V) | ponyDiffusionV6XL |
| Wan 2.1 T2V 1.3B | wai-nsfw-illustrious-v17 |

### 4.5 Wan動画 推奨パラメータ
| パラメータ | 値 |
|-----------|-----|
| 解像度 | 832×480 または 512×512 |
| フレーム数 | 16〜81fr (~5秒) |
| Steps | 20 |
| CFG | 6.0 |
| Scheduler | beta |
| Sampler | euler |

**VRAM消費目安:**
- 512×288 49fr → 2.9GB
- 832×480 81fr → 8.2GB

---

## 5. 顔一貫性 (IPAdapter + FaceID)

### 5.1 手法別使い分け
| 状況 | 手法 | パラメータ |
|------|------|-----------|
| 若い参照から老化 | 低FaceID + 高CFG | FaceID 0.3 / CFG 10.0 |
| 完成形参照を別シーンに転送 | IPAdapterのみ | IPAdapter STANDARD / weight 0.45 |
| 顔＋髪で別の参照が必要 | Dual IPAdapter | FaceID + IPAdapter |

### 5.2 百合子 確定パラメータ
| 年齢 | Doll | DT | FaceID | CFG | 特徴 |
|:----:|:----:|:--:|:------:|:---:|------|
| 18歳 | 0.5 | 0.2 | 0.8 | 7.0 | 通常顔固定 |
| 20歳 | 0.0 | 0.2 | 0.8 | 8.0 | +Dual IPAdapter髪固定 |
| 34歳 | 0.0 | 0.2 | 0.3 | 10.0 | PB: tired eyes/expression |

### 5.3 誠24歳 確定パラメータ
| FaceID | LoRA | CFG | Hair |
|:------:|:----:|:---:|------|
| 0.8 | DetailTweaker 0.2 | 7.0 | 七三分け |
Negativeにfeminine必須。JapaneseDoll不使用。

---

## 6. 動画編集 (FFmpeg MCP)

### 6.1 video_mcp_server.py 利用可能ツール
| ツール名 | 機能 |
|---------|------|
| analyze_media | メディア情報取得（解像度・コーデック・duration） |
| cut_video | 部分切り出し（start/end指定） |
| concat_videos | 複数動画結合（concat demuxer） |
| add_bgm | BGM追加 + ループ + 音量調整（video_volume/bgm_volume） |
| trim_silence | 無音部分自動削除 |
| resize_video | 解像度変更（アスペクト比維持＋パディング） |
| fast_forward | 速度変更（setpts + atempo） |

### 6.2 BGM追加Tips
```powershell
# BGMループ + フェード（直接FFmpeg）
ffmpeg -i video.mp4 -i bgm.mp3 `
  -filter_complex "[1:a]aloop=loop=-1:size=2e9,volume=0.3[bgm];`
                   [0:a]volume=1.0[v];[v][bgm]amix=inputs=2:duration=first[a]" `
  -map 0:v -map "[a]" -c:v copy -y output.mp4
```

---

## 7. AI音楽生成

| ツール | 無料枠 | 品質 | 商用 |
|-------|--------|------|:----:|
| Suno | 1日10曲、クレカ不要 | 業界トップ | 有料プラン |
| Udio | あり | 高品質（特にボーカル） | 有料プラン |
| MusicGen (Meta) | 完全無料（OSS） | BGM用途に十分 | MIT ✅ |
| Mubert | あり | ループBGM特化 | 要確認 |

**おすすめ**: Suno無料で始め、品質確認後に有料 or MusicGen自前ホスト。

---

## 8. opencode (開発環境)

### 8.1 使用Agent一覧
| Agent | 役割 |
|-------|------|
| story-architect | 物語設計・大綱配置・反転設計 |
| character-designer | キャラ設計・言語スタイル・動機連鎖 |
| narrative-writer | **本文執筆のみ**（メインAIは一切書かない） |
| consistency-checker | 事実矛盾スキャン・伏線追跡 |
| story-researcher | 外部資料調査 |
| story-explorer | プロジェクト構造クエリ |
| chapter-extractor | 章抽出・要約 |

### 8.2 鉄則
- **スキルを信じろ。ワークフローを飛ばすな**
- **メインAIは一切書かない**。全工程をAgentに委任
- **設定変更をすぐ本文に反映するな**。変更ログに積んで一括反映
- Gitでバージョン管理: `git add . && git commit -m "メッセージ"`
- セッション開始時は `.active-book` を確認して現在の作品を特定

### 8.3 既知のトラブル
| 症状 | 対処 |
|------|------|
| M2 SSH障害 | `sc.exe create sshd binpath="C:\Windows\System32\OpenSSH\sshd.exe"` |
| M2 Docker停止 | 再接続時に手動起動 |
| ComfyUIクラッシュ | `docker compose down comfyui && docker compose up -d comfyui` |
| opencode YAMLエラー | `.opencode/agents/*.md` のfrontmatter確認 |

---

## 9. 高速化・最適化Tips

- **画像生成**: M2優先（M1の約3倍速: 4秒 vs 12秒）
- **Wan動画**: M1担当（M1にしか5Bモデルがない）
- **SageAttention**: 両機で有効化（`--use-sage-attention`）
- **VOICEVOX**: 話者変更はSPEAKER変数単独変更。chunk間インターバル0.3秒
- **TTS chunk上限500字**: 増やすと合成失敗率上昇。減らすと通信オーバーヘッド増
