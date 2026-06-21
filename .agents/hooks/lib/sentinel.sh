#!/bin/bash
# sentinel.sh — .story-deployed のセンチネルフィールドを読み取るユーティリティ関数
# .story-deployed は YAML key: value 形式（yqに依存せず、awkの単一プロセスで解析）
# 注意：set -euo pipefail は付けない。source 時に呼び出し元の shell options を上書きしないため

sentinel_file() {
  if [ -n "${SENTINEL_FILE:-}" ]; then
    printf '%s\n' "$SENTINEL_FILE"
  elif command -v project_root >/dev/null 2>&1; then
    printf '%s/.story-deployed\n' "$(project_root)"
  else
    printf '%s\n' ".story-deployed"
  fi
}

# read_sentinel_field <field_name> [file]
# フィールド値を出力（前後のスペースとペア引用符を除去）。ファイルまたはフィールドがない場合は空文字列を出力。
# 呼び出し元安全：常に return 0。pipefail / set -e で caller が終了することはない。
read_sentinel_field() {
  local field="$1"
  local file="${2:-$(sentinel_file)}"
  [ -f "$file" ] || return 0
  awk -v key="${field}:" '
    { sub(/\r$/, "") }
    substr($0, 1, length(key)) == key {
      v = substr($0, length(key) + 1)
      sub(/^[[:space:]]+/, "", v)
      n = length(v)
      if (n >= 2 && substr(v, 1, 1) == "\"" && substr(v, n, 1) == "\"") {
        v = substr(v, 2, n - 2)
      } else if (n >= 2) {
        q = sprintf("%c", 39)
        if (substr(v, 1, 1) == q && substr(v, n, 1) == q) {
          v = substr(v, 2, n - 2)
        }
      }
      sub(/[[:space:]]+$/, "", v)
      print v
      exit
    }
  ' "$file" 2>/dev/null
  return 0
}

# sentinel_exists [file] — exit 0 / 1
sentinel_exists() {
  [ -f "${1:-$(sentinel_file)}" ]
}
