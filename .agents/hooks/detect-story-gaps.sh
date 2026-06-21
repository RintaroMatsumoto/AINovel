#!/bin/bash
# detect-story-gaps.sh — 執筆プロジェクトの 5 つのギャップを検出
# 設計原則：ギャップがない場合は完全に沈黙し、何も出力しない。コンテキスト汚染を避ける
set -euo pipefail

# 共通関数ライブラリを読み込み（project_root + discover_all_books）
source "$(dirname "$0")/lib/common.sh"

# 後続のawkで中国語伏線表を解析 + find/grepで中国語パスを処理。Windows中国語システムでGBKロケールが
# エクスポートされている場合、gawkはUTF-8状態値をGBKマルチバイトとしてデコード失敗し、trimや==比較が
# すべて乱れ、各行で誤検出する。強制Cロケールでバイト一致（UTF-8リテラル vs UTF-8コンテンツのバイトが等しい）
# なら安定（issue #164 同類）。本hookはpythonを内蔵していないので、トップで直接export可能。
export LC_ALL=C

ROOT=$(project_root)
OUTPUT=""
HAS_WARNINGS=false

# 1. 新規プロジェクト検出：書名ディレクトリがない（長編と短編プロジェクトの両方をサポート）
# bash 3.2 互換：連想配列を使わず、discover_all_books内部で順序を保持したまま重複排除。
declare -a BOOK_DIRS=()
while IFS= read -r dir; do
  [ -n "$dir" ] && BOOK_DIRS+=("$dir")
done < <(discover_all_books)

if [ "${#BOOK_DIRS[@]}" -eq 0 ]; then
  # 完全な新規プロジェクトで、ディレクトリ構造がない — 静かに終了
  exit 0
fi

for BOOK_DIR in "${BOOK_DIRS[@]}"; do
  BOOK_NAME=$(basename "$BOOK_DIR")
  BOOK_OUTPUT=""

  # 2. 本文は多いが設定が少ない
  CHAPTER_COUNT=0
  SETTING_COUNT=0
  if [ -d "$BOOK_DIR/正文" ]; then
    CHAPTER_COUNT=$(find "$BOOK_DIR/正文" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  elif [ -f "$BOOK_DIR/正文.md" ]; then
    CHAPTER_COUNT=1
  fi
  if [ -d "$BOOK_DIR/设定" ]; then
    SETTING_COUNT=$(find "$BOOK_DIR/设定" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  fi
  if [ "$CHAPTER_COUNT" -gt 10 ] && [ "$SETTING_COUNT" -lt 3 ]; then
    BOOK_OUTPUT+="[WARN] ${BOOK_NAME}：本文 ${CHAPTER_COUNT} 章ですが、設定ファイルは ${SETTING_COUNT} 個のみです。設定の補充を推奨します。\n"
  fi

  # 4. 期限切れまたは異常な伏線
  if [ -f "$BOOK_DIR/追踪/伏笔.md" ]; then
    # テーブルデータ行の状態列のみチェック。正常な開放状態（未埋/已埋）は警告しない。
    # 長編プロジェクトでSessionStartのたびに全伏線監査がトリガーされるのを避ける。
    # 動作回帰スクリプト：scripts/check-hook-regex-sync.sh（ロケール設定の堅牢性は export LC_ALL=C で保証）
    ABNORMAL_FORESHADOW=$(awk -F'|' '
      # 全角スペースU+3000を含む：LC_ALL=Cでは[[:space:]]はASCII空白のみ認識。セルが全角スペースで埋められている場合
      # statusに残って異常と誤判定される。代替で全角スペースを補う（文字グループに入れるとクロスロケールバグを誘発するため）。
      function trim(s) { gsub(/^([[:space:]]|　)+|([[:space:]]|　)+$/, "", s); return s }
      /^\|/ && $0 !~ /^\|[-[:space:]|]+$/ {
        status=trim($6)
        if (status == "" || status == "状态" || status ~ /^状态\{/) next
        if (status == "已过期" || (status != "未埋" && status != "已埋" && status != "已回收")) print
      }
    ' "$BOOK_DIR/追踪/伏笔.md" 2>/dev/null || true)
    if [ -n "$ABNORMAL_FORESHADOW" ]; then
      BOOK_OUTPUT+="[WARN] ${BOOK_NAME}：伏笔.md に期限切れまたは異常な伏線エントリが検出されました。/story-review lean を実行するか、伏線監査を実施してください。\n"
    fi
  fi

  # 5. プロット欠落（プロジェクトタイプごとに判定を分岐）
  if [ -d "$BOOK_DIR/正文" ] || [ -f "$BOOK_DIR/正文.md" ]; then
    # 長編判定：追踪/ がある場合は長編と見なし、大纲/ ディレクトリを要求
    if [ -d "$BOOK_DIR/追踪" ] && [ ! -d "$BOOK_DIR/大纲" ]; then
      BOOK_OUTPUT+="[WARN] ${BOOK_NAME}：正文/ はありますが 大纲/ が不足しています。先にプロットを構築してください。\n"
    # 短編判定：追踪/ がない場合は短編と見なし、小节大纲.md 単一ファイルを要求
    elif [ ! -d "$BOOK_DIR/追踪" ] && [ ! -f "$BOOK_DIR/小节大纲.md" ]; then
      BOOK_OUTPUT+="[WARN] ${BOOK_NAME}：本文はありますが 小节大纲.md が不足しています。先にプロットを構築してください。\n"
    fi
  fi

  # 問題がある場合のみその書籍の情報を出力
  if [ -n "$BOOK_OUTPUT" ]; then
    OUTPUT+="检查：$BOOK_NAME\n$BOOK_OUTPUT"
    HAS_WARNINGS=true
  fi
done

# 3. 全体分析未完了検出（プロジェクトレベル、書籍レベルではない）
GLOBAL_PROGRESS_OUTPUT=""
if [ -d "$ROOT/拆文库" ]; then
  while IFS= read -r -d '' progress_file; do
    GLOBAL_PROGRESS_OUTPUT+="[WARN] 分析未完了：${progress_file#$ROOT/}。実行 /story-long-analyze で続行。\n"
  done < <(find "$ROOT/拆文库" -name "_progress.md" -print0 2>/dev/null || true)
fi
if [ -n "$GLOBAL_PROGRESS_OUTPUT" ]; then
  OUTPUT+="$GLOBAL_PROGRESS_OUTPUT"
  HAS_WARNINGS=true
fi

# 警告がある場合のみ出力
if [ "$HAS_WARNINGS" = true ]; then
  printf '%b' "=== 執筆ギャップ検出 ===\n$OUTPUT\n"
fi
