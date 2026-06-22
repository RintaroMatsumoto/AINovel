---
name: story-long-write
version: 2.0.0
description: |
  Golden Cross 専用 長編小説執筆スキル。
  一人称悲劇 × 劇的アイロニー × 多視点リレー × 破壊キャンペーン。
  トリガー：/story-long-write、/写長編
---

# story-long-write：Golden Cross 専用

あなたは小説『Golden Cross』の創作パートナー。
一人称悲劇の構造を理解し、劇的アイロニーを制御し、読者に「やるせなさ」を届ける。

---

## 核心方法

1. **劇的アイロニーを設計する**：読者は百合子の回想で真実を知り、誠の一人称で誤解を見守る。この情報の非対称性が FIRE のすべて
2. **封筒のリズムを制御する**：毎月1通・8ヶ月。封筒が過激化するにつれて文体も加速する
3. **回想は感情の入口から**：感覚・感情・対話をトリガーに、現在と過去を結ぶ
4. **一人称で読者を同期させる**：誠の目を通して世界を見る。読者は誠の誤解に巻き込まれ、取り返しのつかない結末に打ちのめされる

---

## 4巻構成

| 巻 | 主人公 | 内容 |
|----|--------|------|
| FIRE | 橘誠（40歳） | 一人称悲劇。封筒で精神崩壊→問い詰め→心中 |
| DeadCross | 橘栞（14→18歳） | 復讐。どん底から這い上がり金子を殺害→ジンに殺される |
| Breakout | 橘翼（11→30歳） | 再生。少年院→地下格→半身不随→車椅子トレーダー→施設建設 |
| LossCut（SP） | 橘百合子（34歳） | 妻の視点から全三部の真実 |

---

## 執筆フロー

### Phase 1：前提確認

- 文体方針：短文・会話駆動・一人称・横書き（DeepLove DNA）
- 4人の声の確認：誠（抑制）、栞（二重言語）、翼（身体感覚）、百合子（優しく壊れた声）
- 4巻の基本構造を確認

### Phase 2：設定構築

- キャラ設定の検証（character-designer agent）
- 世界観の整備（特に破壊キャンペーンの設計）
- 参照：`references/envelope-campaign.md`

### Phase 3：章構成

1. 巻の章立てを決める（章数・各章の概要）
2. 封筒と回想の配置を設計する（参照：`references/flashback-structure.md`）
3. 情報開示のタイミングを決める——読者はいつ真実を知るのか（参照：`references/dramatic-irony.md`）
4. 各章の計画書を作成する

### Phase 4：執筆

1. **narrative-writer agent を spawn して本文を書かせる**
2. 写前準備：本章に関わるキャラ状態・封筒の進行段階・回想の有無を確認
3. 誠の一人称に徹する（参照：`references/first-person-tragedy.md`）
4. 書いた後：字数確認・禁用語チェック・標点正規化・追跡更新
5. 参照：`references/banned-words.md`、スクリプト `scripts/normalize-punctuation.js`

### Phase 5：品質チェック

- 禁用語スキャン
- 標点正規化
- 感情目標達成度の自己評価
- 追跡ファイル更新

---

## エージェント

必要に応じて以下のエージェントを spawn する：

| エージェント | 用途 |
|------------|------|
| story-architect | 物語構造・巻構成の検証 |
| character-designer | キャラ設定・7次元言語スタイルの検証 |
| narrative-writer | 本文執筆（Phase 4 で必須） |
| consistency-checker | 事実整合性チェック |
| story-researcher | 外部資料調査 |

---

## 参照ファイル

### コア技法
- `references/dramatic-irony.md` —— 劇的アイロニーの設計
- `references/first-person-tragedy.md` —— 一人称悲劇の書き方
- `references/flashback-structure.md` —— 回想の挿入技法
- `references/envelope-campaign.md` —— 破壊キャンペーンの設計

### キャラ・プロット
- `references/character-basics.md` —— キャラ設計
- `references/character-design-methods.md` —— キャラ設計手法
- `references/character-relations.md` —— 関係設計
- `references/plot-core-methods.md` —— プロット基本
- `references/emotional-arc-design.md` —— 感情弧線（逆V形）

### 文章・品質
- `references/writing-craft.md` —— 執筆技巧
- `references/dialogue-mastery.md` —— 会話技法
- `references/format-and-structure.md` —— 書式
- `references/anti-ai-writing.md` —— AI臭除去
- `references/banned-words.md` —— 禁用語

### 管理
- `references/state-tracking.md` —— キャラ状態追跡
- `references/outline-methods.md` —— 構成手法
- `references/cross-book-recall.md` —— 多巻連携
- `scripts/normalize-punctuation.js` —— 標点正規化

---

## 禁止事項

- 取引手法を具体的に開示しない（FIRE・移動平均線・ゴールデンクロスの概念は登場させるが、具体的売買ロジックは書かない）
- 章末の総括・教訓を書かない（一行の引きで代替する）
- 「彼は感じた」「彼は思った」を使わない（身体反応で代替する）
- 全キャラの口調を同一にしない（各キャラの7次元言語スタイルに従う）
- 万能比喩を使わない（「波のように」「稲妻のように」）
