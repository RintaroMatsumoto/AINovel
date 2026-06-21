#!/bin/bash
# session-end.sh — セッション終了時に必要に応じて最終状態を記録
# 設計原則：デフォルトでは沈黙しファイルを書き込まない。明示的に有効化しても短編プロジェクトの 追踪/ ディレクトリは作成しない
set -euo pipefail

# 共通関数ライブラリを読み込み
source "$(dirname "$0")/lib/common.sh"

# バイト安定領域：discover_active_book で中国語書名/パスを処理。GBK ロケール下でも乱れない（issue #164 同類）。
export LC_ALL=C

# デフォルトでは session-log.txt の書き込みを無効（毎回のセッション終了時にワークツリーを汚染しないため）。
# 明示的に STORY_SESSION_LOG=1 の場合のみ有効。有効でも、既存の長編追跡ディレクトリにのみ書き込む。
if [ "${STORY_SESSION_LOG:-0}" != "1" ]; then
  exit 0
fi

BOOK_DIR=$(discover_active_book)

# 既存の追跡ディレクトリにのみ書き込む。mkdir はしない。短編プロジェクトを誤って長編構造に昇格させないため。
if [ -n "$BOOK_DIR" ] && [ -d "$BOOK_DIR/追踪" ]; then
  echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')] session ended" >> "$BOOK_DIR/追踪/session-log.txt"
fi
