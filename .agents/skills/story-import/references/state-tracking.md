# 状態追跡プロトコル

Phase 3 パイプライン処理中に状態を追跡し、各処理単位の進捗記録を保持する統一プロトコル。

## 状態ファイルの位置

状態ファイルは `分析庫/{書名}/_state.json` に配置。

## 状態フィールド定義

```json
{
  "bookTitle": "原書名",
  "importId": "uuid",
  "pipelinePhase": "1|2|3",
  "currentPhase": "phase-1|phase-2|phase-3",
  "steps": {
    "phase-1": {
      "status": "completed|in_progress|pending",
      "completedAt": "ISO 日時",
      "artifacts": ["本書基本情報.md", "リソース請求.json"]
    },
    "phase-2": {
      "status": "completed|in_progress|pending",
      "completedAt": "ISO 日時",
      "artifacts": ["文字数/ジャンル分析.md", "段落構造分析.md"]
    },
    "phase-3": {
      "status": "completed|in_progress|pending",
      "completedAt": "ISO 日時",
      "route": "short|long",
      "artifacts": ["設定/...", "本文/...", "追跡/..."]
    }
  },
  "errors": [],
  "totalChars": 0,
  "wordCount": 0
}
```

## 状態更新ルール

- 各 Phase 完了時に状態を更新
- Phase 移行前に現在 Phase の全成果物が存在することを検証
- エラー発生時は `errors` 配列に記録
- エラー復旧時は `errors` から削除

## 再開可能プロトコル

状態ファイルが存在する場合：
1. 現在 Phase を読み取り、途中からの再開を判断
2. 存在する成果物は再生成しない
3. ユーザーに現在進捗を確認

## 品質チェックリスト

- [ ] 状態ファイルが `_state.json` に保存されている
- [ ] 状態フィールド定義が完全
- [ ] Phase 値が正しく更新されている
- [ ] `errors` 配列に未解決のエラーがない
