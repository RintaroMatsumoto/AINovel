# ComfyUI 画像生成ツール

小説DayTradeのキャラ画像をM1 Mac Mini（Docker ComfyUI）で生成するGUIツール。

## 動作概要

Windowsデスクトップアプリ（exe単体）。M1のComfyUI APIにリクエストを投げ、画像を`Desktop/output/`に保存する。

## ビルド方法（ソースからexeを作る）

### 必要なもの
- Python 3.10（プロジェクト内にインストール済み: `AppData\Local\Programs\Python\Python310\`）
- PyInstaller（初回のみインストール）

### 手順

```powershell
# 1. PyInstallerインストール（初回のみ）
& "C:\Users\GoldRush\AppData\Local\Programs\Python\Python310\python.exe" -m pip install pyinstaller

# 2. ソースからビルド
& "C:\Users\GoldRush\AppData\Local\Programs\Python\Python310\python.exe" -m PyInstaller --onefile --noconsole "novels\生成\comfyui_gen_tool.py"

# 3. 出力された dist\comfyui_gen_tool.exe をデスクトップに配置
Copy-Item "dist\comfyui_gen_tool.exe" "Desktop\ComfyUI_画像生成.exe"

# 4. 後片付け
Remove-Item -Recurse "build" -Force
Remove-Item -Recurse "dist" -Force
Remove-Item "comfyui_gen_tool.spec" -Force
```

### 注意点
- exeを上書きするときは旧exeを**事前に終了**しておく（ファイルロックで上書き失敗する）
- タスクマネージャーか `taskkill /f /im "ComfyUI*.exe"` で強制終了してから上書き

## 使い方

1. `Desktop\ComfyUI_画像生成.exe` をダブルクリック起動
2. M1 Mac MiniのComfyUIが起動していることを確認（http://100.112.59.35:18188）
3. 「ランダム生成」でプロンプトを自動作成 → 「生成」で画像生成
4. 生成画像は `Desktop/output/` に保存される

### SFW / NSFW切替

| モード | プロンプト | ネガティブ | カテゴリ選択 |
|--------|-----------|-----------|------------|
| SFW | 通常キーワードのみ | `nude, exposed` 含む | 非表示 |
| NSFW | 部位タグ・カテゴリキーワード追加 | `nude, exposed` 除去 | 表示（チェック可） |

### NSFWカテゴリ（チェックボックス）

| カテゴリ | 追加されるキーワード例 |
|---------|---------------------|
| まんこ(pussy) | pussy, spread pussy, labia, open pussy |
| ヴァギナ(vagina) | vagina, vaginal opening |
| クリトリス(clitoris) | clitoris, detailed clitoris, clit |
| モリマン | raised mons pubis, cameltoe |
| 透けマン | see-through panty, wet panty |
| 断面図(inside) | inside of vagina, close up |
| 中出し(cum) | cum, creampie, cum inside |

チェックなし → bodyパーツからランダム抽出（従来動作）

## 接続先

- ComfyUI API: `http://100.112.59.35:18188`
- モデル: `yayoi_mix.safetensors` (SD1.5)
- LoRA: JapaneseDollLikeness_v15 (0.5) + DetailTweaker (0.2)
- 解像度: 512×768 / Steps: 28 / CFG: 7.0 / Sampler: dpmpp_2m / Scheduler: karras

## ソース

`novels/生成/comfyui_gen_tool.py` — 自由に編集して再ビルド可能。
