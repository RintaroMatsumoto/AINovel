# セッション記録 — 2026-07-11/12

> 目的: 同業他社調査 → AI画像小説YouTubeチャンネルの戦略策定
> 参加: ユーザー + opencode (deepseek-v4-flash)
> モード: plan → build

---

## 1. 競合調査結果

### 1.1 日本語圏AI朗読チャンネルの実態

- **主流は「完全自動化・大量生産」路線**（TubeGen.ai + ElevenLabs）
- 動画尺は**10〜60分の長尺**が主力。Shortsは導線で本命は長尺
- 最大のリスクは**「再利用されたコンテンツ」ポリシー**による収益化剥奪
- 競合の大半はAI生成 or 著作権切れ作品 → **オリジナルIPが最大の差別化要因**

### 1.2 英語圏（参考）

- 「Faceless YouTube Channel」市場、全新規クリエイターの38%
- 主ジャンル: True Crime / Horror / Finance / Animal Rescue
- RPMは日本語圏の**3〜5倍**（$10-30）
- ElevenLabs一強。VOICEVOX/AivisSpeechのような無料OSSは無い
- 2025年7月ポリシーで低品質AI量産チャンネルは軒並み収益化剥奪

### 1.3 決定した方針

| 軸 | 判断 |
|----|------|
| 当面の市場 | **日本語圏**に集中 |
| 英語圏 | **将来的に展開視野**（翻訳＋キャラ差し替え＋11Labs） |
| 戦略ポジション | **高品質・オリジナルIP・低コスト**（競合の量産型と差別化） |

---

## 2. AivisSpeech Engine 導入

### 2.1 M1マシン構成

| 項目 | 実態 |
|------|------|
| IP | 100.112.59.35 |
| OS | **Windows 10**（build 26200、日本語版）← Linuxだと思ってたが違った |
| CPU | AMD Ryzen Threadripper 2990WX (32C/64T) |
| RAM | 64GB |
| GPU | RTX 3060 12GB / Driver 596.36 / CUDA 13.2 |
| Docker | Docker Desktop + WSL2（Linuxコンテナモード） |
| 稼働中コンテナ | comfyui (m1-stable) :18188, open-webui, ollama |

### 2.2 Dockerセットアップ

**コンテナ**: `aivisspeech`（cpu-latest）
**ポート**: 10101
**状態**: 常時稼働中（`--restart=unless-stopped`）
**モデル配置先**: `C:\Users\admin\AppData\Roaming\AivisSpeech-Engine\Models\`

```
docker run -d --restart=unless-stopped --name aivisspeech \
  -p 10101:10101 \
  -v "%USERPROFILE%\AppData\Roaming\AivisSpeech-Engine:/home/user/.local/share/AivisSpeech-Engine-Dev" \
  ghcr.io/aivis-project/aivisspeech-engine:cpu-latest
```

**注意**: Docker Desktop + WSL2環境でSSH経由の`docker pull`は認証エラーになる。
→ 回避策として**Scheduled Taskからバッチを実行**してpull/runする。
→ dll認証が必要な場合も同様。

### 2.3 認証問題の解決方法

Windows + Docker Desktop + WSL2 では、SSH経由での`docker pull`が`error getting credentials`で失敗する。
原因は`credsStore: desktop`がWindows対話型セッションを必要とするため。

**解決策**: Scheduled Task（スケジュールタスク）経由で実行する。

```powershell
# バッチファイルを作成 → Scheduled Taskで実行
schtasks /create /sc once /tn PullAivis /tr "C:\path\to\script.bat" /st 00:00 /ru admin /rp admin /f
schtasks /run /tn PullAivis
schtasks /delete /tn PullAivis /f
```

**single download は SSH 直でも成功する**（PowerShellのInvoke-WebRequest）が、複数DLには不向き。

---

## 3. 音声モデル

### 3.1 インストール済み22モデル

**男性系（ナレーション向け）**:
| モデル | 声質 | スタイル数 | Style ID (ノーマル) |
|--------|------|:---------:|:-----------------:|
| **阿井田 茂** | **中年男性** ★推奨 | **7** | 1310138976 |
| fumifumi | 壮年男性 | 1 | 606865152 |
| ろてじん（長老） | 熟年男性 | 1 | 391794336 |
| ろてじん（匿名） | 中年男性 | 1 | 1805828384 |
| にせ | 若い男性 | 1 | 1937616896 |
| kuroike ai | 若い男性 | 5 | 1553803492 |

**女性系**:
| モデル | 声質 | スタイル数 | Style ID (ノーマル) |
|--------|------|:---------:|:-----------------:|
| まお | 若い女性 | 6 | 888753760 |
| コハク | 若い女性 | 4 | 1878365376 |
| みちのくあいり | 若い女性 | **7**（感情豊富） | 1717361472 |
| リダ/Lida | 若い女性 | **10**（最多） | 1349521248 |
| 凛音エル | 若い女性 | 5 | 1388823424 |
| まい | 若い女性 | 1 | 1431611904 |
| 花音 | 若い女性 | 1 | 1325133120 |
| るな | 若い女性 | 1 | 345585728 |
| 桜音 | 若い女性 | 1 | 376644064 |
| morioki | 壮年女性 | 1 | 497929760 |

**中性・特殊**:
| モデル | 声質 | スタイル数 | Style ID |
|--------|------|:---------:|:--------:|
| らせつん | **中性** | **8** | 893625024 |
| 六弦エレキ | 機械音/環境音 | 4 | 436195520 |

**T2系（実験的）**:
黄金笑_T2 / 七日週_T2 / 大日椛_T2 / 葉土此_T2（各3スタイル）

### 3.2 商用利用可否

| ライセンス | モデル | 扱い |
|--------|------|------|
| **ACML 1.0** | 上記のうち17モデル | ✅ **商用OK、クレジット不要** |
| **Custom** | リダ/Lida | ✅ **商用OK、ただしクレジット必須**（話者名＋URL） |
| **Custom（Tプロジェクト）** | 七日週_T2 / 大日椛_T2 / 葉土此_T2 | ✅ 商用OK、利用規約に同意 |
| **ACML-NC** | kuroike ai | ❌ **非商用のみ** |

### 3.3 テスト音声

- 全22モデルのノーマルスタイルで同一台本（プロローグ118字）を合成済み
- 保存先: `C:\Users\GoldRush\AppData\Local\Temp\aivis_test\`
- ファイル名: `{話者名}_{スタイル名}.wav`（各〜16-28秒）
- **まだ聴き比べていない**。後日聴いて1つに絞る

---

## 4. BGM

### 4.1 方針

- **定番の無料BGM**を使用（AI生成は使わない）
- **感情トーン4つ**に1曲ずつ選定、動画内で切り替えて使う（4曲全部使う）
- 切り替えルール: シーン転換で、文の途中では変えない。クロスフェード推奨

### 4.2 ソース

| ソース | 商用 | クレジット | 曲数 |
|--------|:---:|:---------:|:----:|
| **魔王魂** (maou.audio) | ✅ | 推奨（任意） | 21曲DL済み |
| **DOVA-SYNDROME** (dova-s.jp) | ✅ | 曲による | 未DL（SPAのため個別DL推奨） |
| **甘茶の音楽工房** | ✅ | 必要 | 未DL |
| **YouTube Audio Library** | ✅ | 曲による | 保険 |

### 4.3 4トーン選曲

| # | トーン | 使用曲 | 使用シーン例 |
|:-:|:------|--------|------------|
| 1 | **穏やか・温かい** | `acoustic52_ast_daily_sound.mp3` | 家族の食卓、日常 |
| 2 | **悲しみ・回想** | `piano37_セピアの風.mp3` | 百合子の回想、栞の過去 |
| 3 | **不安・緊張** | `piano36_宿命のシナリオ.mp3` | 誠の決意、不穏な伏線 |
| 4 | **崩壊・衝撃** | `orchestra26_戦いの跡.mp3` | クライマックス、真実の発覚 |

`golden_cross_theme.mp3` は**将来のフルAI動画ドラマ用**で、読み上げ動画では使わない。

### 4.4 全BGMファイル

`_素材/` 配下に25曲。内訳:
- 既存: 4曲（bgm_loud, bgm_prologue, golden_cross_theme, hitohiki）
- 魔王魂ピアノ: 10曲
- 魔王魂オーケストラ: 6曲
- 魔王魂アコースティック: 5曲

### 4.5 DOVA-SYNDROME未DLの理由

DOVA-SYNDROMEが**SPA（JavaScriptレンダリング）**のため、プログラムからの一括DLが不可能。
後日ブラウザから個別DL推奨。推奨曲:
- Recollections / Morning / 10℃ / パステルハウス（日常）
- 遥かな想い / ランタン / 星空へ浮かぶランタン（回想）
- 傷心のピアノ / 不気味なランタン（緊張）
- ウィンドチャンプ（やや明るめ）

---

## 5. 残タスク

| 優先度 | タスク | 備考 |
|:-----:|--------|------|
| 🔴 | **22モデルの聴き比べ** | テストWAVを聴いてナレーター声を1つに決める |
| 🔴 | **config.py 修正** | BASE → `http://100.112.59.35:10101`、SPEAKER → 選んだモデルのStyle ID |
| 🟡 | **第1章テスト動画制作** | AivisSpeech + BGM + 挿絵で1本通しで作る |
| 🟡 | **競合レポートにAivisSpeech情報を統合** | docs/competitor_analysis.md 更新 |
| 🟢 | DOVA-SYNDROMEから追加BGMをDL | ブラウザで個別DL |
| 🟢 | 英語圏展開の準備 | GoldenCrossの英語翻訳着手（将来） |

---

## 6. 作成したドキュメント一覧

| ファイル | 内容 |
|---------|------|
| `docs/competitor_analysis.md` | 競合調査レポート（SWOT分析、推奨アクション） |
| `docs/aivisspeech_models.md` | AivisSpeech音声モデル台帳（22モデル詳細） |
| `docs/bgm_catalog.md` | BGM台帳（選曲基準、4トーン選定、全ファイル一覧） |
| `docs/session_summary.md` | **本ファイル。セッション全体の記録** |

---

## 7. 技術的ハマりポイント（次回の自分へ）

### 7.1 Docker Desktop + WSL2 + SSH認証問題

**症状**: SSH経由で`docker pull ghcr.io/...` が `error getting credentials` で失敗
**原因**: `credsStore: desktop`（Docker Desktopの資格情報ヘルパー）がWindows対話セッションを必要とする
**解決策**: Scheduled Taskを経由してバッチ実行

**二度目へのアドバイス**: 
1. `schtasks /create` + `schtasks /run` でScheduled Task経由実行
2. バッチファイルを別途作成しておく
3. 単発のInvoke-WebRequestはSSH直でも成功する

### 7.2 DOVA-SYNDROMEはSPA

検索もダウンロードもJavaScript依存。プログラマティックな一括取得は困難。
→ 素直にブラウザで個別DLするのが最速。

### 7.3 魔王魂はRefererチェックあり

直接MP3リンクにアクセスすると403 Forbidden。
→ `Referer: https://maou.audio/category/bgm/bgm-piano/` ヘッダーが必要。
→ ブラウザでは普通にDLできる（Referer自動付与のため）。

### 7.4 PowerShellのcp932問題

PowerShellの出力で日本語が文字化けする（cp932のため）。
ファイル名や内容自体は正しく保存されているので実害なし。
どうしても気になる場合は `[Console]::OutputEncoding = [Text.Encoding]::UTF8` を設定。

---

## 8. キーデータ（よく使う値）

```python
# M1 (AivisSpeech Engine)
AIVIS_BASE = "http://100.112.59.35:10101"

# M2 (ComfyUI)
COMFYUI_HOST = "100.107.17.85"
COMFYUI_PORT = 18188

# AivisSpeech Docker管理
# 再起動: docker restart aivisspeech
# モデル追加: .aivmx を Models/ にコピー → docker restart
# Modelsディレクトリ: C:\Users\admin\AppData\Roaming\AivisSpeech-Engine\Models\
```
