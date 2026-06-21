#!/bin/bash
# validate-story-commit.sh — git commit 時にフォーマット問題をチェック（WARNINGのみ、BLOCKINGなし）
set -euo pipefail

source "$(dirname "$0")/lib/common.sh"

HOOK_INPUT="${CLAUDE_TOOL_INPUT:-}"
if [ -z "$HOOK_INPUT" ] && [ ! -t 0 ]; then
  HOOK_INPUT="$(cat)"
fi
export HOOK_INPUT

is_git_commit_command() {
  # 実際に使用可能なインタプリタを検出：Windows上で `command -v python3` はMicrosoft Store
  # スタブ（exit 49）にヒットするため、PATHを確認するだけでなく実際に -c "" を実行する必要がある。
  local PYBIN=""
  for c in python3 python py; do
    if "$c" -c "" >/dev/null 2>&1; then PYBIN="$c"; break; fi
  done
  [ -z "$PYBIN" ] && return 1
  "$PYBIN" - <<'PY'
import json
import os
import re
import shlex
import sys

raw = os.environ.get("STORY_COMMIT_COMMAND", "")
if not raw:
    hook_input = os.environ.get("HOOK_INPUT", "")
    if not hook_input:
        sys.exit(1)
    try:
        obj = json.loads(hook_input)
    except Exception:
        obj = {}

    def find_command(value):
        if isinstance(value, dict):
            for key in ("command", "cmd", "script"):
                if isinstance(value.get(key), str):
                    return value[key]
            for key in ("tool_input", "input", "parameters", "args"):
                found = find_command(value.get(key))
                if found:
                    return found
        return ""

    raw = find_command(obj)

if not raw:
    sys.exit(1)

# Bash treats unescaped newlines like command separators; normalize them before
# shlex tokenization so multi-line Bash tool inputs still expose later git commits.
raw = raw.replace("\r\n", "\n").replace("\r", "\n").replace("\n", " ; ")

try:
    lexer = shlex.shlex(raw, posix=True, punctuation_chars="();|&{}")
    lexer.whitespace_split = True
    tokens = list(lexer)
except TypeError:
    try:
        tokens = shlex.split(raw, posix=True)
    except Exception:
        tokens = raw.split()
except Exception:
    tokens = raw.split()

if not tokens:
    sys.exit(1)

assignment = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
separators = {";", "&&", "||", "|", "|&", "&"}
openers = {"(", "{"}
closers = {")", "}"}
control_words = {"then", "do", "else", "elif"}
wrappers = {"command", "noglob"}
git_options_with_value = {
    "-C", "-c", "--git-dir", "--work-tree", "--namespace",
    "--exec-path", "--super-prefix", "--config-env",
}

def skip_shell_wrappers(i):
    while i < len(tokens):
        tok = tokens[i]
        if tok in openers:
            i += 1
            continue
        if assignment.match(tok):
            i += 1
            continue
        if tok in wrappers:
            i += 1
            continue
        if tok == "env":
            i += 1
            while i < len(tokens):
                if assignment.match(tokens[i]):
                    i += 1
                    continue
                if tokens[i] in {"-i", "--ignore-environment"}:
                    i += 1
                    continue
                break
            continue
        break
    return i

def is_git_commit_at(i):
    if i >= len(tokens) or tokens[i] != "git":
        return False
    i += 1
    while i < len(tokens):
        tok = tokens[i]
        if tok in closers or tok in separators:
            return False
        if tok == "commit":
            return True
        if tok == "--":
            i += 1
            continue
        if tok in git_options_with_value:
            i += 2
            continue
        if any(tok.startswith(prefix + "=") for prefix in git_options_with_value if prefix.startswith("--")):
            i += 1
            continue
        if tok.startswith("-c") and tok != "-c":
            i += 1
            continue
        if tok.startswith("-"):
            i += 1
            continue
        return False
    return False

segment_start = True
i = 0
while i < len(tokens):
    tok = tokens[i]
    if tok in separators or tok in control_words:
        segment_start = True
        i += 1
        continue
    if segment_start or tok in openers:
        start = skip_shell_wrappers(i)
        if is_git_commit_at(start):
            sys.exit(0)
        segment_start = False
    i += 1

sys.exit(1)
PY
}

# PreToolUse matcher が広すぎるか、ターゲットCLIが if フィールドをサポートしていない可能性がある。スクリプトは内部で自己チェックする必要がある。
# 明確な git commit コマンドがない場合は完全に静かに終了。echo/grep などのコマンドの誤トリガーを避ける。
if ! is_git_commit_command; then
  exit 0
fi

# 後続の case + grep で中国語パス/本文内容をマッチング。Windows中国語システムでGBKロケールが
# エクスポートされている場合、grepはUTF-8コンテンツをGBKマルチバイトとしてデコードし文字化けする。
# 強制Cロケールでバイト一致すれば安定（issue #164 同類）。
# is_git_commit_command（内蔵python）の後に配置し、その入力デコードに影響しないようにする。
export LC_ALL=C

ROOT=$(project_root)
GIT_ROOT=$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null || printf '%s\n' "$ROOT")
WARNINGS=""

# コミット予定のファイルリストを取得（-z null区切りでスペースパス問題を回避）
while IFS= read -r -d '' file; do
  # md ファイル以外はスキップ
  case "$file" in
    *.md) ;;
    *) continue ;;
  esac

  FULL_PATH="$ROOT/$file"
  if [ ! -f "$FULL_PATH" ]; then
    FULL_PATH="$GIT_ROOT/$file"
  fi

  # 本文ファイルにハードコードされたプロット値が含まれていないかチェック
  # コロン/空白は全角文字を角括弧文字グループに入れるのではなく、代替を使用。全角文字を含む文字グループはCロケールで
  # シングルバイトに分解され、マッチ漏れする。(：|:) は全角「：」と半角「:」の両方にヒット、([[:space:]]|　) は LC_ALL=C 下で
  # 全角スペース U+3000 も認識する（そうしないと全角スペース区切りの記述が漏検出/誤判定される）。
  case "$file" in
    正文.md|*/正文.md|正文/*|*/正文/*)
      HARDCODED=$(grep -nE "(身高|体重|年龄)([[:space:]]|　)*(：|:)([[:space:]]|　)*[0-9]+" "$FULL_PATH" 2>/dev/null || true)
      if [ -n "$HARDCODED" ]; then
        WARNINGS="$WARNINGS\n⚠ $file: Hardcoded character attributes found (should reference 设定/ files):\n$HARDCODED"
      fi
      ;;
  esac

  # 設定ファイルの必須フィールドをチェック（構造化マッチング：key:value 形式）
  case "$file" in
    设定/*|*/设定/*)
      if ! grep -qE "^([[:space:]]|　)*(名字|姓名|名称|name|Name)([[:space:]]|　)*(：|:)" "$FULL_PATH" 2>/dev/null; then
        WARNINGS="$WARNINGS\n⚠ $file: Setting file missing required fields (name/名字: ...)"
      fi
      ;;
  esac
done < <(git -C "$ROOT" -c core.quotepath=false diff --cached --relative --name-only --diff-filter=ACM -z -- . 2>/dev/null || true)

if [ -n "$WARNINGS" ]; then
  echo "=== Story Commit Warnings (advisory only, not blocking) ==="
  printf '%b\n' "$WARNINGS"
  echo "=== End Warnings ==="
fi

# 常に exit 0 — 執筆フローが hook で止められてはいけない
exit 0
