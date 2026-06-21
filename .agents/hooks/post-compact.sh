#!/bin/bash
# post-compact.sh — compact 後にコンテキスト復元を促す
set -euo pipefail

# 共通関数ライブラリを読み込み
source "$(dirname "$0")/lib/common.sh"

# バイト安定領域：discover_active_book で中国語書名/パスを処理。GBK ロケール下でも乱れない（issue #164 同類）。
export LC_ALL=C

ROOT=$(project_root)
BOOK_DIR=$(discover_active_book)

if [ -n "$BOOK_DIR" ] && [ -f "$BOOK_DIR/追踪/上下文.md" ]; then
  LINE_COUNT=$(wc -l < "$BOOK_DIR/追踪/上下文.md" | tr -d ' ')
  echo "Context was compacted. Read ${BOOK_DIR#$ROOT/}/追踪/上下文.md ($LINE_COUNT lines) to restore writing context."
else
  echo "Context was compacted. Check 追踪/上下文.md to restore context."
fi
