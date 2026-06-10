# AINovel パイプライン

## 概要
AIと協力して小説を書くための統合パイプライン。

## 使用可能なSkill（コマンド）
- `/story-setup` または `準備写書` - 環境セットアップ
- `/story` または `網文` - スキルルーター
- `/story-long-write` または `写長編` - 長編執筆
- `/story-long-analyze` - 長編分析（構成・リズム分析）
- `/story-long-scan` - 長編市場調査
- `/story-short-write` - 短編執筆
- `/story-short-analyze` - 短編分析
- `/story-short-scan` - 短編市場調査
- `/story-deslop` または `去AI味` - AI臭除去
- `/story-import` または `導入小説` - 既存作品の取込
- `/story-review` または `審査` - 複数視点でのレビュー
- `/story-cover` または `封面` - 表紙生成

## MCPサーバー
- `sequential-thinking` - プロット構築・段階的問題解決
- `memory` - ナレッジグラフ記憶（登場人物・設定）
- `filesystem` - ファイル操作

## ディレクトリ構造
```
長編/{作品名}/
  設定/世界観/  設定/キャラクター/  設定/勢力/
  プロット/  本文/  参考/  追跡/
短編/
分析庫/
ナレッジ/
```

## 執筆フロー
1. `/story-setup` で環境準備
2. `/story-long-scan` で市場調査
3. `/story-long-analyze` で参考作品分析
4. `/story-long-write` で執筆（プロット→設定→本文）
5. `/story-deslop` でAI臭除去
6. `/story-review` でレビュー

Gitで各バージョンを管理: `git add . && git commit -m "第X章 完了"`
