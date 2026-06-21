---
name: browser-cdp
description: "Use this skill when you need to control a Chrome browser via CDP (Chrome DevTools Protocol) to reuse existing login sessions. Covers: launching Chrome in debug mode, opening URLs, waiting for page load, evaluating JavaScript, taking snapshots, and extracting auth tokens. Trigger phrases: browser automation, CDP, agent-browser, 浏览器操作, 操作浏览器, Chrome CDP, 复用登录态, extract token from browser."
metadata:
  openclaw:
    requires:
      bins:
        - agent-browser
    source: https://github.com/worldwonderer/oh-story-claudecode
---

# Browser CDP 操作ツール

CDP プロトコルで Chrome を制御し、既存のログイン状態を再利用してブラウザ自動化操作を実行します。

## 前提条件

- macOS / Linux / Windows（実験的）、Google Chrome がインストール済み
- Node.js 12+
- `agent-browser` インストール済み：`npm install -g agent-browser`

> ⚠️ **初回起動時に通常の Chrome を強制終了します。** 起動前に必ずユーザーの同意を得てください（下記「起動フロー」参照）。同意なしに実行すると、ユーザーが未保存のタブや下書きを失う可能性があります。

---

## 起動フロー（skill-mode 必須手順）

**第一步：現在の状態を確認（副作用なし）**

```bash
node {SKILL_DIR}/scripts/setup-cdp-chrome.js 9222 --detect-only
```

出力例：

```
CDP_STATUS=ready                        # 準備完了、直接利用可能
CDP_URL=http://127.0.0.1:9222/json/version
BROWSER=Chrome/148.0.7778.168
```

または：

```
CDP_STATUS=needs-setup
CHROME_RUNNING=yes                      # ユーザーの Chrome が稼働中、起動すると強制終了する
CHROME_PID_COUNT=3
```

**第二步：検出結果に応じて分岐**

- `CDP_STATUS=ready` → 直接 `agent-browser --cdp 9222 ...` を使用。**setup を実行しない**。
- `CDP_STATUS=needs-setup` かつ `CHROME_RUNNING=no` → 安全に起動：
  ```bash
  node {SKILL_DIR}/scripts/setup-cdp-chrome.js 9222 --yes
  ```
- `CDP_STATUS=needs-setup` かつ `CHROME_RUNNING=yes` → **AskUserQuestion ツールでユーザーに確認**：N 個の Chrome プロセスを強制終了すること、未保存作業が失われる可能性を伝える；同意を得てから `--yes` 付きで起動；拒否された場合は自動化を中止。

**なぜ直接 `--yes` できないのか：** スクリプトは非 TTY（すなわち skill モード / Bash ツール）で、Chrome が稼働中かつ `--yes` なしの場合、終了コード 3 で `NEEDS_CONSENT: ...` を出力して中断します。これは意図的な安全策ですが、skill フローは終了コード 3 を見て無条件に `--yes` を渡すのではなく、先にユーザーに確認する必要があります。

---

## 起動スクリプトオプション

| オプション | 説明 |
|------|------|
| `--detect-only` | 検出のみ、状態を変更しない（skill 用） |
| `--yes` | 同意取得済み、対話型プロンプトをスキップ |
| `--reset` | 起動前に `~/chrome-debug-profile` をクリア（ログイン失効時） |
| `--profile <name>` | デフォルト以外の Chrome profile を使用（例 `"Profile 1"`） |
| `--dry-run` | 実行する手順を表示するのみ、実行しない |

終了コード：`0` 成功 / `1` 一般エラー / `2` ユーザー拒否（TTY）/ `3` 同意が必要だが `--yes` なし。

---

## よく使う操作

### ページを開いて読み込みを待つ

```bash
agent-browser --cdp 9222 open "<URL>"
agent-browser --cdp 9222 wait 3000
```

### ページテキストの抽出

```bash
agent-browser --cdp 9222 eval 'document.body.innerText.substring(0, 8000)'
```

### Auth Token の抽出

```bash
agent-browser --cdp 9222 eval 'localStorage.getItem("token") || document.cookie'
```

### 複雑な JS（引用符 / `$` / バッククォートを含む）

シェルのエスケープは失敗しやすいため、以下のいずれかの方法を使用：

```bash
# 1) base64 ラップ
agent-browser --cdp 9222 eval -b "$(echo -n "document.querySelectorAll('a').length" | base64)"

# 2) heredoc + --stdin
cat <<'EOF' | agent-browser --cdp 9222 eval --stdin
const links = document.querySelectorAll('a');
links.length;
EOF
```

### ページ操作（snapshot で要素参照を取得）

```bash
agent-browser --cdp 9222 snapshot -i        # 操作可能要素のみ
agent-browser --cdp 9222 click "<CSS or @e1>"
agent-browser --cdp 9222 type "<sel>" "<text>"
```

---

## 停止 / クリーンアップ

- debug Chrome ウィンドウを閉じる（または `pkill -9 -x 'Google Chrome'` / `taskkill /F /IM chrome.exe`）。
- ログイン状態失効：`node {SKILL_DIR}/scripts/setup-cdp-chrome.js 9222 --reset --yes`（`--yes` も同様に事前にユーザー確認が必要）。

---

## よくある問題

| 問題 | 解決策 |
|------|----------|
| `NEEDS_CONSENT` + 終了コード 3 | AskUserQuestion で Chrome 強制終了の許可を得て、同意後 `--yes` 付きで再実行 |
| CDP ポートがリッスンしていない | `--detect-only` で再確認；ポートが占有されている場合はポートを変更 |
| ページがログインページにリダイレクト | `snapshot -i` でログインボタンを探して操作 |
| `eval` が `null` を返す | localStorage key 名を確認；引用符を含む JS は `eval -b` または `--stdin` を使用 |
| ログイン状態が期限切れ | `setup-cdp-chrome.js 9222 --reset --yes` で再コピー |
| 複数の Chrome profile がある | `--profile "Profile 1"` で指定 |
| Chrome が起動しない（30秒タイムアウト） | `--reset` を試す；ポート競合を確認；`~/chrome-debug-profile/` が破損していないか確認 |
