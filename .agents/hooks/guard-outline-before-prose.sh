#!/bin/bash
# guard-outline-before-prose.sh — PreToolUse(Write|Edit|MultiEdit) フローガード
# 「正文」を書く前に対応するプロット/詳細プロットが必要。なければ阻止（exit 2、BLOCKING）。
#
# 以下の場合のみブロック：「初めて本文ファイルを作成し、詳細プロットがない」
#   - 長編 正文/第N章_*.md ：同書の 大纲/細綱_第N章.md の存在が必要
#   - 短編 正文.md         ：同ディレクトリの 小节大纲.md の存在が必要
# 本文が既に存在する場合（続き/去AI味/改稿）はすべて通過。非本文ターゲット、パスが解析できない場合は静かに通過。
# 設計原則：誤検出より見逃しを優先——不確実な場合はすべて exit 0。
set -euo pipefail

source "$(dirname "$0")/lib/common.sh"

# 全行程バイト安定領域：本hookは中国語パスでbashワイルドカードを使用（中間ディレクトリが中国語書名の場合
# 細綱_第*章*.md はGBKロケールでNOMATCH）、sedで章番号抽出、caseマッチング、pythonを内蔵して
# 中国語パスを抽出する。Windows中国語システムでGBK/GB2312ロケールがエクスポートされている場合、
# これらはすべてマルチバイトとしてUTF-8を誤ってデコードし、機能しなくなる。強制Cロケールでバイト一致
# （UTF-8リテラル vs UTF-8バイトが等しい）なら安定（issue #164）。
# 内蔵pythonの前にexportする必要あり：LC_ALL=C下のpythonはWindowsでUnicode環境APIを使用し、
# 新しいpythonはCを強制的にUTF-8に変換するため、中国語入力を正しくデコードできる。むしろユーザーのGBKロケールが
# pythonが読んだUTF-8環境変数を文字化けさせる。出力はsys.stdout.bufferでUTF-8バイトを直接書き込み、ロケールに依存しない。
export LC_ALL=C

HOOK_INPUT="${CLAUDE_TOOL_INPUT:-}"
if [ -z "$HOOK_INPUT" ] && [ ! -t 0 ]; then
  HOOK_INPUT="$(cat)"
fi
export HOOK_INPUT

# tool入力JSONからターゲットファイルパスを抽出。実際に使用可能なインタプリタを検出：Windows上で
# `command -v python3` はMicrosoft Storeスタブ（exit 49）にヒットするため、PATHを確認するだけでなく
# 実際に -c "" を実行する。
# 出力はsys.stdout.bufferでUTF-8バイトを直接書き込み：Windows中国語システムのpython stdoutはデフォルトで
# cp936、テキストモード出力は中国語パスをGBKにエンコードし、スクリプト内のUTF-8リテラル（"正文"、第N章）と
# バイトが一致せず、すべての比較が恒偽になり、ガードが静かに通過する（issue #164）。
extract_target_path() {
  local PYBIN=""
  for c in python3 python py; do
    if "$c" -c "" >/dev/null 2>&1; then PYBIN="$c"; break; fi
  done
  [ -z "$PYBIN" ] && return 1
  "$PYBIN" - <<'PY'
import json, os, sys

raw = os.environ.get("HOOK_INPUT", "")
if not raw:
    sys.exit(1)
try:
    obj = json.loads(raw)
except Exception:
    sys.exit(1)

def dig(value):
    if isinstance(value, dict):
        for k in ("file_path", "path", "filePath"):
            v = value.get(k)
            if isinstance(v, str) and v:
                return v
        for k in ("tool_input", "input", "parameters", "args"):
            found = dig(value.get(k))
            if found:
                return found
    return ""

p = dig(obj)
if not p:
    sys.exit(1)
sys.stdout.buffer.write(p.encode("utf-8"))
PY
}

TARGET="$(extract_target_path 2>/dev/null || true)"
# パスが解析できない → 通過
[ -z "$TARGET" ] && exit 0

ROOT=$(project_root)
case "$TARGET" in
  /*) ABS="$TARGET" ;;
  *)  ABS="$ROOT/$TARGET" ;;
esac

BASE="$(basename "$ABS")"
PARENT="$(basename "$(dirname "$ABS")")"

case "$BASE" in
  正文.md)
    # 短編単一ファイル本文：既存なら通過（続き/改稿）
    [ -f "$ABS" ] && exit 0
    BOOK_DIR="$(dirname "$ABS")"
    # story-import 移行：既に 拆文库/{書名}/ 分析ソースがある場合、本文が小节大纲より先に移行するのは正常フロー（小节大纲は分析から逆算）なので通過
    [ -d "$ROOT/拆文库/$(basename "$BOOK_DIR")" ] && exit 0
    # 確実に短編プロジェクトの場合のみブロック（设定.md 信号あり——story-short-write/import は先に 设定.md を生成）、
    # docs/正文.md などの非作品ファイルを誤ってブロックしない
    [ -f "$BOOK_DIR/设定.md" ] || exit 0
    if [ ! -f "$BOOK_DIR/小节大纲.md" ]; then
      printf '%s\n' "⛔ 本文書き込みがブロックされました：${TARGET} に同ディレクトリの 小节大纲.md がありません。" >&2
      printf '%s\n' "   story-short-write に従って「小节大纲.md」を先に作成し、その後本文を書いてください（プロットなしで本文を書くことは許可されていません）。" >&2
      printf '%s\n' "   どうしても先に下書きが必要な場合は、小节大纲.md を先に作成してください。" >&2
      exit 2
    fi
    ;;
  *)
    # 長編分割本文：親ディレクトリは「正文」、ファイル名は 第N章... の形式
    [ "$PARENT" = "正文" ] || exit 0
    case "$BASE" in
      第*章*.md) ;;
      *) exit 0 ;;
    esac
    # 既存なら通過（続き/改稿）
    [ -f "$ABS" ] && exit 0
    # 章番号（先頭ゼロ除去）
    NUM="$(printf '%s' "$BASE" | sed -n 's/^第0*\([0-9][0-9]*\)章.*/\1/p')"
    [ -z "$NUM" ] && exit 0
    BOOK_DIR="$(dirname "$(dirname "$ABS")")"
    # story-import 移行：既に 拆文库/{書名}/ 分析ソースがある場合は通過（細綱は章要約から逆算され、本文より後に移行）
    [ -d "$ROOT/拆文库/$(basename "$BOOK_DIR")" ] && exit 0
    OUTLINE_DIR="$BOOK_DIR/大纲"
    FOUND=""
    if [ -d "$OUTLINE_DIR" ]; then
      # ゼロ埋めの差異とタイトル接尾辞を許容：整数章番号で 大纲/細綱_第*章*.md を一致
      for f in "$OUTLINE_DIR"/细纲_第*章*.md; do
        [ -e "$f" ] || continue
        fnum="$(basename "$f" | sed -n 's/^细纲_第0*\([0-9][0-9]*\)章.*/\1/p')"
        if [ "$fnum" = "$NUM" ]; then FOUND="$f"; break; fi
      done
    fi
    if [ -z "$FOUND" ]; then
      printf '%s\n' "⛔ 本文書き込みがブロックされました：第 ${NUM} 章に細綱がありません（${OUTLINE_DIR#$ROOT/}/細綱_第${NUM}章.md）。" >&2
      printf '%s\n' "   story-long-write の単章フローに従って細綱を先に作成し、その後本文を書いてください（細綱なしで直接書くことは許可されていません）。" >&2
      printf '%s\n' "   どうしても先に下書きが必要な場合は、対応する細綱ファイルを先に作成してください。" >&2
      exit 2
    fi
    ;;
esac

exit 0
