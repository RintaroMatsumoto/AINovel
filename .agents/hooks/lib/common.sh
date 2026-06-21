#!/bin/bash
# common.sh — 共通関数ライブラリ。各 hook ファイルから source される
# 注意：set -euo pipefail は付けない。source 時に呼び出し元の shell options を上書きしないため

# project_root — プロジェクトルートを安定して解析
# 優先順位：Claude Code が注入した CLAUDE_PROJECT_DIR → git root → カレントディレクトリ。
# 絶対パスを出力。hook がネストされた cwd から実行された場合の誤読/誤書きを防止。
project_root() {
  if [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ -d "$CLAUDE_PROJECT_DIR" ]; then
    (cd "$CLAUDE_PROJECT_DIR" 2>/dev/null && pwd -P) && return
  fi
  local git_root
  git_root=$(git rev-parse --show-toplevel 2>/dev/null || true)
  if [ -n "$git_root" ] && [ -d "$git_root" ]; then
    (cd "$git_root" 2>/dev/null && pwd -P) && return
  fi
  pwd -P
}

# resolve_project_path <path> — 将相对路径按项目根目录解析为绝对路径。
resolve_project_path() {
  local path="$1"
  case "$path" in
    /*) printf '%s\n' "$path" ;;
    *) printf '%s/%s\n' "$(project_root)" "$path" ;;
  esac
}

# discover_active_book — 単一書籍照会（アクティブな書籍）
# 優先順位：root/.active-book → find で最初の 追踪/ (長編) または 正文/ / 正文.md (短編) ディレクトリ。
# 使用シーン：session-start / session-end / pre-compact / post-compact —— 1セッションで現在アクティブな1冊のみに関心。
discover_active_book() {
  local root
  root=$(project_root)

  if [ -f "$root/.active-book" ]; then
    local active
    # LC_ALL=C：書名は中国語UTF-8。Windows中国語システムでGBKロケールがエクスポートされている場合、trimの
    # s/^[[:space:]]*// はsedにGBKとして行全体をデコードさせ、短い書名（例「让你管账号」「修仙传」）の
    # UTF-8バイトは不正なGBKシーケンスとなる→BSD sedがillegal byte sequenceを報告、activeが空に→
    # .active-book が無視され、findで見つかった最初の書籍に誤解析される。強制Cロケールでバイト処理すれば安定。
    # 本ライブラリはexportなしのsession-*/pre-compact/post-compactで再利用されるため、ここでコマンド単位でフォールバックし、
    # ライブラリ内ではexportしない（呼び出し元にグローバル副作用を残さないため。ファイルヘッダの「呼び出し元のshellオプションを上書きしない」と一致）。
    active=$(LC_ALL=C sed -n '1p' "$root/.active-book" | LC_ALL=C sed 's/^[[:space:]]*//;s/[[:space:]]*$//' || true)
    if [ -n "$active" ]; then
      resolve_project_path "$active"
      return
    fi
  fi

  # 長編優先（追踪/ ディレクトリが存在）
  local first
  first=$(find "$root" -maxdepth 4 -type d -name "追踪" -print -quit 2>/dev/null || true)
  if [ -n "$first" ]; then
    dirname "$first"
    return
  fi

  # 短編フォールバック：正文/ ディレクトリまたは 正文.md を検索（maxdepth 4 で 推薦/短編/書名/正文 構造をカバー）
  local story_path
  story_path=$(find "$root" -maxdepth 4 \( -type d -name "正文" -o -type f -name "正文.md" \) -print -quit 2>/dev/null || true)
  if [ -n "$story_path" ]; then
    dirname "$story_path"
  fi
}

# discover_all_books — 複数書籍照会（プロジェクト内の全書籍）
# 出力：改行区切りの絶対ディレクトリパスリスト（重複なし）。
# 使用シーン：detect-story-gaps —— プロジェクト内の全書籍を走査してギャップ検出を行う。
discover_all_books() {
  local root
  root=$(project_root)
  # awkで重複排除し挿入順を保持（bash 3.2互換、連想配列不使用）
  {
    # 長編：追踪/ の親ディレクトリ
    find "$root" -maxdepth 4 -type d -name "追踪" -print 2>/dev/null | while IFS= read -r d; do dirname "$d"; done
    # 短編：正文/ の親ディレクトリ または 正文.md の親ディレクトリ
    find "$root" -maxdepth 4 \( -type d -name "正文" -o -type f -name "正文.md" \) -print 2>/dev/null | while IFS= read -r d; do dirname "$d"; done
  } | awk 'NF && !seen[$0]++'
}

# 旧名エイリアス。外部カスタムhookからの参照用。新コードは discover_active_book / discover_all_books を使用。
discover_book_dir() {
  discover_active_book "$@"
}
