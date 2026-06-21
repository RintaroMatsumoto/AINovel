#!/bin/bash
# session-start.sh — プロジェクト状態と執筆コンテキストの概要表示
# 設計原則：利用可能な情報がない場合は完全に沈黙し、何も出力しない。コンテキスト汚染を避ける
set -euo pipefail

HOOK_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT=""
HAS_CONTENT=false

# 最小限のpreflightを先に実行し、その後source。そうしないとlib欠落時に修復可能なヒントを出力できない。
if [ ! -f "$HOOK_DIR/lib/common.sh" ] || [ ! -f "$HOOK_DIR/lib/sentinel.sh" ]; then
  printf '%b' "[WARN] story hook 関数ライブラリが不足しています。再実行 /story-setup で .claude/hooks/lib/ を復元してください。\n"
  exit 0
fi

# 共通関数ライブラリを読み込み
source "$HOOK_DIR/lib/common.sh"
source "$HOOK_DIR/lib/sentinel.sh"

# バイト安定領域：このhookはdiscover_active_bookで中国語の書名/パスを処理する。Windows中国語システムで
# GBKロケールがエクスポートされている場合、ロケール依存操作はUTF-8をマルチバイトとして誤ってデコードする。強制的にCロケールでバイト処理すれば安定（issue #164
# 同類）。本hookはpythonを内蔵していないので、直接export可能。
export LC_ALL=C

ROOT=$(project_root)

# story-setup デプロイ後の一度限りの再起動確認。custom agentsはセッション起動時にのみ
# subagent_typeとして登録される。story-setupのデプロイ完了後、.claude/.agents-pending-restartマーカーが残る。
# ここまで来たということは新セッションであり、agentsはセッションとともに再読み込み済み——確認してマーカーをクリア（一度限り）。
if [ -f "$ROOT/.claude/.agents-pending-restart" ]; then
  OUTPUT+="[INFO] story-setup が agents をデプロイ/更新しました。本セッションは再読み込み済み——story-architect、narrative-writer 等の custom agent が登録され利用可能です。\n"
  OUTPUT+="  執筆 skill がまだ spawn 失敗 / solo 降格を表示する場合、デプロイ時の古いセッションにいる可能性があります。新しい Claude Code セッションを開き直してください。\n\n"
  HAS_CONTENT=true
  rm -f "$ROOT/.claude/.agents-pending-restart" 2>/dev/null || true
fi

# デプロイ自己チェック：.story-deployed は存在するが hooks ファイルが誤って削除された場合に警告
if sentinel_exists "$ROOT/.story-deployed"; then
  MISSING_HOOKS=""
  for hook in session-start.sh session-end.sh detect-story-gaps.sh pre-compact.sh post-compact.sh validate-story-commit.sh guard-outline-before-prose.sh lib/common.sh lib/sentinel.sh; do
    if [ ! -f "$ROOT/.claude/hooks/$hook" ]; then
      MISSING_HOOKS+="$hook "
    fi
  done
  if [ -n "$MISSING_HOOKS" ]; then
    OUTPUT+="[WARN] .story-deployed は存在しますが hook が不足：$MISSING_HOOKS\n"
    OUTPUT+="  修復：再実行 /story-setup で不足している hook を復元してください。\n\n"
    HAS_CONTENT=true
  fi

  AGENTS_VERSION=$(read_sentinel_field agents_version "$ROOT/.story-deployed")
  case "$AGENTS_VERSION" in
    ''|*[!0-9]*)
      OUTPUT+="[WARN] .story-deployed に数字の agents_version がありません。再実行 /story-setup。\n\n"
      HAS_CONTENT=true
      ;;
    *)
      if [ "$AGENTS_VERSION" -lt 13 ]; then
        OUTPUT+="[WARN] story-setup agents_version=$AGENTS_VERSION が v13 未満です。再実行 /story-setup で hooks、agents、references を更新してください（デプロイ後は新セッションが必要）。\n\n"
        HAS_CONTENT=true
      fi
      ;;
  esac

  for field in setup_skill_version target_cli resolver_strategy references_dir; do
    if [ -z "$(read_sentinel_field "$field" "$ROOT/.story-deployed")" ]; then
      OUTPUT+="[WARN] .story-deployed に $field フィールドがありません。再実行 /story-setup でデプロイメタ情報を更新してください。\n\n"
      HAS_CONTENT=true
    fi
  done

  REFERENCES_DIR=$(read_sentinel_field references_dir "$ROOT/.story-deployed")
  if [ -n "$REFERENCES_DIR" ]; then
    REFERENCES_PATH=$(resolve_project_path "$REFERENCES_DIR")
    if [ ! -d "$REFERENCES_PATH" ] || ! find "$REFERENCES_PATH" -maxdepth 1 -type f -name "*.md" -print -quit 2>/dev/null | grep -q .; then
      OUTPUT+="[WARN] story-setup の参照資料パッケージが不足しているか空です：${REFERENCES_DIR}。再実行 /story-setup。\n\n"
      HAS_CONTENT=true
    fi
  fi
else
  OUTPUT+="[WARN] 執筆環境がデプロイされていません。実行 /story-setup で初期化してください。\n\n"
  HAS_CONTENT=true
fi

# ブランチと最近のコミットを表示（git 履歴がある場合のみ）
BRANCH=$(git -C "$ROOT" branch --show-current 2>/dev/null || echo "")
if [ -n "$BRANCH" ]; then
  OUTPUT+="=== 写作进度 ===\n"
  OUTPUT+="分支：$BRANCH\n"
  RECENT=$(git -C "$ROOT" log --oneline -5 2>/dev/null || true)
  if [ -n "$RECENT" ]; then
    OUTPUT+="$RECENT\n"
  fi
  OUTPUT+="\n"
  HAS_CONTENT=true
fi

# 上下文.md の要約（現在位置のみ、先頭10行）
BOOK_DIR=$(discover_active_book)
if [ -n "$BOOK_DIR" ] && [ -f "$BOOK_DIR/追踪/上下文.md" ]; then
  OUTPUT+="--- 当前位置 ---\n"
  SNAPSHOT=$(head -10 "$BOOK_DIR/追踪/上下文.md")
  OUTPUT+="${SNAPSHOT}\n---\n\n"
  HAS_CONTENT=true
fi

# 未完了の分析（閾値 > 0 の場合のみ報告）
if [ -d "$ROOT/拆文库" ]; then
  PROGRESS_COUNT=$(find "$ROOT/拆文库" -name "_progress.md" 2>/dev/null | wc -l | tr -d ' ')
  if [ "$PROGRESS_COUNT" -gt 0 ]; then
    OUTPUT+="[INFO] 拆文库/ に $PROGRESS_COUNT 件の未完了分析があります。実行 /story-long-analyze または /story-short-analyze。\n"
    HAS_CONTENT=true
  fi
fi

# 実際の内容がある場合のみ出力。それ以外は完全に沈黙
if [ "$HAS_CONTENT" = true ]; then
  printf '%b' "$OUTPUT"
fi
