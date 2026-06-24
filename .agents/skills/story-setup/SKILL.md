---
name: story-setup
version: 1.2.2
description: |
  網文ライティングツールセットのインフラストラクチャデプロイ。hooks/rules/agents/CLAUDE.md などのインフラをユーザープロジェクトにデプロイする。
  トリガー方法：/story-setup、「本を書く準備」「環境を整えて」「ライティングプロジェクトを設定」
metadata:
  openclaw:
    source: https://github.com/worldwonderer/oh-story-claudecode
---

# story-setup：網文ライティングツールセット インフラストラクチャデプロイ

あなたはライティングインフラストラクチャデプロイヤーです。網文ライティングツールセットの全インフラ（hooks、rules、agents、CLAUDE.md）をユーザープロジェクトにデプロイします。

**絶対ルール：ユーザーの既存設定を上書きせず、マージして置き換える。**

---

## Phase 1：プロジェクト状態の検出

1. 現在のディレクトリが既にデプロイ済みか確認（`.story-deployed` の存在）
   - 既にある場合 → AskUserQuestion で再デプロイするか確認
2. 書名ディレクトリ（`追跡/` サブディレクトリを含むディレクトリ、またはユーザー定義構造）があるか確認
   - あり → 長編プロジェクトとして認識、現在のプロジェクト情報を表示
   - なし → 新規プロジェクトまたは短編プロジェクトとして認識
3. `.claude/settings.local.json` の存在確認
   - あり → 既存設定を読み込み、後でマージ
   - なし → 後で新規ファイルを作成
4. `.active-book` ファイルの存在確認
   - あり → 現在のアクティブ書名を表示
   - なし → スキップ

## Phase 2：インフラストラクチャデプロイ

AskUserQuestion でデプロイ位置を確認後、順次実行。

### 2.0 デプロイリスト（機械的にチェック可能）

| Source path | Target path | Owner class | Merge mode | Validation check |
|-------------|-------------|-------------|------------|------------------|
| `skills/story-setup/references/templates/CLAUDE.md.tmpl` | `CLAUDE.md` | user+managed | marker/section merge | contains story skill routing sections |
| `skills/story-setup/references/templates/hooks/` | `.claude/hooks/` | story-setup managed | recursive replace | `session-*.sh`, `detect-story-gaps.sh`, `validate-story-commit.sh`, `guard-outline-before-prose.sh`, `lib/common.sh`, `lib/sentinel.sh` exist |
| `skills/story-setup/references/templates/rules/*.md` | `.claude/rules/*.md` | story-setup managed | replace | every rule contains `paths` frontmatter |
| `skills/story-setup/references/templates/agents/*.md` | `.opencode/agents/*.md` | story-setup managed | replace | 7 agent files exist |
| `skills/story-setup/references/agent-references/*.md` | `.claude/skills/story-setup/references/agent-references/*.md` | story-setup managed | replace | every `story-setup/references/agent-references/*.md` reference resolves |
| `skills/story-setup/references/templates/settings-hooks.json` | `.claude/settings.local.json` | user+managed | merge by hook command | hook JSON valid and registered commands deduped |
| `skills/story-setup/references/templates/上下文.md.tmpl` | `{書名}/追跡/上下文.md` | user state | create only if absent | never overwrite existing writing context |
| generated sentinel | `.story-deployed` | story-setup managed | replace | contains `agents_version`, `setup_skill_version`, `target_cli`, `resolver_strategy`, `references_dir` |

### 2.1 CLAUDE.md のデプロイ

- `skills/story-setup/references/templates/CLAUDE.md.tmpl` を読み込み
- プレースホルダーを置換（下記「テンプレートプレースホルダー」参照）
- プロジェクトルート `CLAUDE.md` に書き込み（既存の場合は「CLAUDE.md マージ戦略」に従って処理）

### 2.2 Hooks のデプロイ

- **ディレクトリツリーを再帰的にコピー**：`skills/story-setup/references/templates/hooks/` をユーザープロジェクトの `.claude/hooks/` にコピー
- サブディレクトリ `lib/` を保持する必要あり：
  - `lib/common.sh` は `project_root`、`discover_active_book`、`discover_all_books` を提供
  - `lib/sentinel.sh` は `.story-deployed` フィールドの読み取りを提供
- `.claude/hooks/*.sh` にのみ実行権限を設定（`chmod +x`）；`lib/*.sh` は hook が `source` するため、実行ビットは不要

### 2.3 Rules のデプロイ

- `skills/story-setup/references/templates/rules/` 下の全 `.md` ファイルを読み込み
- ユーザープロジェクトの `.claude/rules/` ディレクトリにコピー

### 2.4 Agents のデプロイ

- `skills/story-setup/references/templates/agents/` 下の全 `.md` ファイルを読み込み
- ユーザープロジェクトの `.opencode/agents/` ディレクトリにコピー
- Agent ファイルは story-setup 管理ファイルのため、安全に上書き可能；バージョンアップ時は `UPGRADING.md` のバージョン検出結果に従って再デプロイ
- **デプロイ後は必ず新しいセッションを開くこと**：Claude Code はセッション起動時に `.opencode/agents/` をスキャンして subagent を登録する。現在のセッション内で新しくデプロイされた agent はすぐには利用不可——ユーザーは新しい Claude Code セッションを開く必要があり、そうして初めて `story-architect`/`narrative-writer` などのカスタム agent が `subagent_type` として登録される；そうしないと、story-review、story-long-write などが spawn しようとしたときに「subagent_type が利用不可」となり solo（単一視点）にフォールバックする。この手順はインストールレポートで必ず明示的にユーザーに伝えること（Phase 3 第 6 ステップ参照）。

### 2.4.1 Agent 互換性処理

- Agent frontmatter は Claude Code を基準とする；OpenClaw/qclaw などは AgentSkills をサポートしていれば、未知のフィールド（`memory`、`skills`、`disallowedTools` など）は無視される。ターゲットツールが frontmatter エラーを報告した場合は、`name`、`description`、`tools` の 3 項目を保持し、サポート外のフィールドを削除してからデプロイする。
- プロジェクトにデプロイ後、agent 内で参照する資料は `story-setup/references/agent-references/*.md` という本 skill 内のコピーパスを経由すること；他の skill の references を横断参照しない。グローバルインストールパスが異なる場合は、プロジェクト内の `.claude/skills/` または `skills/` を優先的なパスプレフィックスとし、次にツールの skill 検索能力を使用し、固定の絶対パスを仮定しない。

### 2.4.2 Agent References のデプロイ

- `skills/story-setup/references/agent-references/` 下の全 `.md` をプロジェクト内 `.claude/skills/story-setup/references/agent-references/` にコピー
- ターゲットプロジェクトが既にプロジェクトローカルの `skills/` ディレクトリを使用している場合、`skills/story-setup/references/agent-references/` にもフォールバックとして同期コピーできるが、フォールバックのみにコピーして `.claude/skills/` のメインパスを欠落させてはならない
- 検証：agent または reference 内に `story-setup/references/agent-references/<file>.md` が出現した場合、ソースパッケージとターゲットパッケージの両方に `<file>.md` が存在しなければならない

### 2.5 Session State テンプレートのデプロイ

- `skills/story-setup/references/templates/上下文.md.tmpl` を読み込み
- 長編書目として認識され、かつ `{書名}/追跡/` が既に存在する場合のみ、不足している `{書名}/追跡/上下文.md` を作成
- ターゲットファイルが既に存在する場合は上書きしない；短編プロジェクトではこれにより `追跡/` ディレクトリを作成してはならない

### 2.6 Hooks 登録を settings.local.json にマージ

> 互換性注意：`settings-hooks.json` 内の PreToolUse の `if` フィールドは Claude Code hook 条件構文を使用しており、hook-level if をサポートする実行環境が必要です。ターゲットツールがこのフィールドをサポートしない場合、hook スクリプト自体がセルフチェックを行い advisory-only で終了します；デプロイ時にこの `if` フィールドを削除し、matcher + command を保持しても構いません。

- `skills/story-setup/references/templates/settings-hooks.json` を読み込み
- ユーザープロジェクトの `.claude/settings.local.json`（存在する場合）を読み込み
- hooks 設定をマージ（「settings-hooks.json マージアルゴリズム」に従って処理）
- `.claude/settings.local.json` に書き込み

### 2.7 デプロイマークの作成

- `.story-deployed` ファイル（sentinel file）を作成
- 以下のフィールドを書き込み（YAML `key: value` 形式、hook は `references/templates/hooks/lib/sentinel.sh` で読み取り）：
  ```
  deployed_at: <date -u +"%Y-%m-%dT%H:%M:%SZ">
  agents_version: 13
  setup_skill_version: 1.2.2
  target_cli: claude-code
  resolver_strategy: project-local-skill-reference
  references_dir: .claude/skills/story-setup/references/agent-references
  ```
- このファイルは session-start.sh および執筆 skill がデプロイ状態を検出し、重複プロンプトを回避するために使用
- 同時に一回限りのマークファイル `.claude/.agents-pending-restart`（空ファイルで可）を作成。session-start.sh は次のセッション起動時、これにより agents が新しいセッションで登録されたことを確認し、自動的にこのマークを削除——ユーザーに「再起動が有効になった」ことを伝える
- `.story-deployed` が既に存在するが `agents_version` がない、またはバージョン < 13 の場合、story-setup の再実行を促し hooks/agents/rules/reference bundle を更新する（具体的な変更は `UPGRADING.md` 参照）

## Phase 3：インストール検証

1. hooks 登録の検証：
   - `.claude/settings.local.json` 内の hooks フィールドが正しいか確認
   - `.claude/hooks/` 下のスクリプトが存在し、実行権限があるか確認
   - `.claude/hooks/lib/common.sh` と `.claude/hooks/lib/sentinel.sh` が存在するか確認
2. rules パスの検証：
   - `.claude/rules/` 下のルールファイルが存在し、`paths` frontmatter を含むか確認
3. agents の検証：
   - `.opencode/agents/` 下の 7 つの agent 定義ファイルが存在するか確認
4. agent reference bundle の検証：
   - `.claude/skills/story-setup/references/agent-references/` 下の reference ファイルが完全か確認
   - すべての `story-setup/references/agent-references/<file>.md` がデプロイされた bundle に解決できるか確認
5. デプロイマークの検証：
   - `.story-deployed` が存在し、タイムスタンプ、`agents_version: 13`、`setup_skill_version: 1.2.2`、`target_cli`、`resolver_strategy`、`references_dir` を含むか確認
6. インストールレポートを出力：
   - デプロイ済みの全ファイルをリスト
   - 注意すべき事項をリスト（既存設定がマージされた場合など）
   - **⚠️ 再起動プロンプト（目立つように出力すること）**：今回のデプロイで `.opencode/agents/` に書き込みを行いましたが、これらのカスタム agent は「セッション起動時」にのみ Claude Code によって `subagent_type` として登録されます。**執筆を開始する前に新しい Claude Code セッションを開いてください**。そうしないと、現在のセッションでは story-review / story-long-write などが `story-architect`、`narrative-writer` などを spawn しようとしたときに「subagent_type が利用不可」となり solo（単一視点、マルチエージェント協働を失う）にフォールバックします。効果があったかどうかの判断：新しいセッションで `/story-review` を実行し、レポートヘッダーが `Effective Mode: full/lean` なら登録成功；`Fallback: ... -> solo` ならまだ古いセッションか未登録です。
   - 再起動後、`/story-long-write` または `/story-short-write` が使用可能

---

## テンプレートプレースホルダー

| プレースホルダー | 置換ルール | 例 |
|--------|----------|------|
| `{プロジェクト名}` | ユーザープロジェクト名またはディレクトリ名 | 「剣来」、「暗衛」 |
| `{書名}` | 書名ディレクトリ名（ディレクトリと一致） | `{プロジェクト名}` と同じ、またはユーザー定義 |
| `{ターゲットプラットフォーム}` | ターゲット公開プラットフォーム | 起点、番茄、晋江、知乎塩選 |
| `{作者名}` | ユーザーのペンネームまたはニックネーム | 未指定時は「作者」 |

置換時は中括弧を削除。ユーザーがプロジェクト名を指定しない場合、現在のディレクトリ名を使用する。未指定のプレースホルダーはそのまま保持し、置換しない。

## CLAUDE.md マージ戦略

ユーザーが既に CLAUDE.md を持っている場合、marker/section でマージ：
1. story-setup 管理ブロックのマークを優先的に識別（旧プロジェクトにマークがあれば、マーク内のコンテンツのみ置換）
2. マークがない場合、ユーザーの既存 CLAUDE.md を読み込み、`##` 見出しで section map に分割
3. テンプレート CLAUDE.md.tmpl を読み込み、同様に分割
4. テンプレート内の標準 section（Skill ルーティングテーブル、ファイル構造、協働ルール、Context Recovery、言語）はユーザーの同名 section を**上書き**
5. ユーザー固有の section（カスタムコンテンツ）はそのまま**保持**
6. 不明な競合は AskUserQuestion でユーザーにどちらのバージョンを残すか選択させる

## settings-hooks.json マージアルゴリズム

hooks 登録マージは command フィールドで重複排除：
1. ユーザーの既存 `.claude/settings.local.json`（存在する場合）を読み込み、hooks 部分を抽出
2. `settings-hooks.json` テンプレートを読み込み、登録する hooks を抽出
3. 各 hook event（SessionStart、PreToolUse など）に対して：
   - ユーザーが既に持っている hook command → 保持、重複追加しない
   - テンプレート内の新しい hook command → 対応する event の hooks 配列に append
   - ユーザー固有のその他の設定（permissions、env など）→ 完全に保持
4. マージ後の完全な settings.local.json を書き込み

## 再デプロイ

- `.story-deployed` が存在しない → 新規インストール、Phase 2 を全て実行
- `.story-deployed` が存在し `agents_version: 13` → デプロイ済みを表示、AskUserQuestion で再デプロイするか確認
- `.story-deployed` が存在するが `agents_version` < 13 → アップデートが必要と表示、Phase 2 を再実行して agents/hooks/rules/reference bundle を上書き、CLAUDE.md と settings.local.json はマージ戦略を適用

---

## 参考资料

| ファイル | 用途 |
|------|------|
| references/templates/CLAUDE.md.tmpl | プロジェクトルート CLAUDE.md テンプレート |
| references/templates/hooks/ | 7 つの hook スクリプトテンプレート + `lib/common.sh`/`lib/sentinel.sh` |
| references/templates/rules/ | 4 つの path-scoped ルールテンプレート |
| references/templates/agents/ | 7 つの agent 定義テンプレート（story-architect, character-designer, narrative-writer, consistency-checker, story-researcher, story-explorer, chapter-extractor） |
| references/agent-references/ | Agent テンプレートに付属する参考资料のコピー；`.claude/skills/story-setup/references/agent-references/` にデプロイし、他 skill の references への横断参照を回避 |
| references/templates/settings-hooks.json | hooks 登録 JSON 断片 |
| references/templates/上下文.md.tmpl | 執筆コンテキストテンプレート |

---

## フロー連携

**パイプライン：** デプロイ
**位置：** 初期化（最優先）

| タイミング | ジャンプ先 | コマンド |
|---|---|---|
| デプロイ完了、執筆開始 | story-long-write / story-short-write | `/story-long-write` または `/story-short-write` |
| 既存小説をインポートして分析 | story-import | `/story-import` |
| ブラウザのログイン状態が必要（スキャン/分析で原文取得） | browser-cdp | `/browser-cdp` |
