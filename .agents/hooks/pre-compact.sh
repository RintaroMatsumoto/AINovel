#!/bin/bash
# pre-compact.sh — compact 前に執筆状態の要約を記録（内容はダンプしない）
set -euo pipefail

# 共通関数ライブラリを読み込み
source "$(dirname "$0")/lib/common.sh"

# バイト安定領域：discover_active_book で中国語書名/パスを処理。GBK ロケール下でも乱れない（issue #164 同類）。
export LC_ALL=C

ROOT=$(project_root)

echo "=== Pre-Compact Summary ==="

BOOK_DIR=$(discover_active_book)

# 上下文.md の状態要約（パス + 行数、内容は出力しない）
if [ -n "$BOOK_DIR" ] && [ -f "$BOOK_DIR/追踪/上下文.md" ]; then
  LINE_COUNT=$(wc -l < "$BOOK_DIR/追踪/上下文.md" | tr -d ' ')
  echo "Writing context: ${BOOK_DIR#$ROOT/}/追踪/上下文.md ($LINE_COUNT lines)"
else
  echo "Active state: not found"
fi

# Git 未コミット変更数
CHANGED=$(git -C "$ROOT" diff --name-only 2>/dev/null | wc -l | tr -d ' ') || CHANGED=0
STAGED=$(git -C "$ROOT" diff --name-only --cached 2>/dev/null | wc -l | tr -d ' ') || STAGED=0
echo "Git: ${CHANGED} unstaged, ${STAGED} staged"

echo "=== Pre-Compact Complete ==="
