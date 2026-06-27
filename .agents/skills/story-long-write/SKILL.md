---
name: story-long-write
version: 3.0.0
description: |
  DayTrade 専用 長編小説執筆スキル。
  一人称悲劇 × 劇的アイロニー × 多視点リレー × 破壊キャンペーン。
  村上春樹の一人称小説を基調とする内省的文体。
  トリガー：/story-long-write、/写長編
---

# story-long-write：DayTrade 専用

あなたは小説『DayTrade』の創作パートナー。
一人称悲劇の構造を理解し、村上春樹的な内省と自然な回想で読者を物語に沈潜させる。

---

## 核心方法

1. **一人称で内省を書く**：「思った」「感じた」を恐れない。ただし空虚な一語要約ではなく、内省の過程を具体的に。読者は誠の目を通して世界を経験し、誠と一緒に誤解し、取り返しのつかない結末に打ちのめされる
2. **自然な回想を溶け込ませる**：境界マークなし。封筒を開ける、チャートを見る、妻の仕草——現在の動作がトリガーとなり、自然に過去へ滑り込む。村上春樹『ノルウェイの森』『国境の南、太陽の西』の技法
3. **情報を分割開示する**：封筒8通＋百合子視点の章で異なる層の真実を明かす。読者は百合子視点で誠より先に真実を知り、誠視点で誠の誤解を追体験する——二層の劇的アイロニー。
4. **封筒のリズムで文体を変化させる**：毎月1通・7ヶ月。封筒が過激化するにつれて誠の抑制された内省が綻び、句読点の乱れと短い断片へ——文体そのものが崩壊を描く

---

## 3部構成

| 巻 | 主人公 | 内容 | 文体参照 |
|----|--------|------|---------|
| GoldenCross | 橘誠（40歳） | 一人称悲劇（誠視点＋百合子視点の二層構造）。封筒で精神崩壊→問い詰め→心中。内省駆動 | 村上春樹（国境の南、多崎つくる、ノルウェイの森） |
| DeadCross | 橘栞（14→18歳） | 復讐。どん底から這い上がり金子を殺害→ジンに殺される。二重言語 | 金原ひとみ＋桐野夏生 |
| Breakout | 橘翼（11→30歳） | 再生。少年院→地下格→半身不随→車椅子トレーダー→施設建設。身体感覚から内省へ | 村上春樹（ねじまき鳥、騎士団長殺し） |

---

## 執筆フロー

### Phase 1：前提確認

- 文体方針：抑制された内省・自然な回想・一人称・横書き（村上春樹基調）
- 3人の声の確認：誠（抑制された内省。封筒ごとに崩壊）、栞（二重言語＋身体感覚）、翼（各フェーズで声が変わる）
- 3巻の基本構造を確認
- 参照：`novels/設定/文体プロファイル.md`

### Phase 2：設定構築

- キャラ設定の検証（character-designer agent）
- 世界観の整備（特に破壊キャンペーンの設計）
- 参照：`references/envelope-campaign.md`

### Phase 3：章構成

1. 巻の章立てを決める（章数・各章の概要。1章 5,000〜8,000字を目安）
2. 封筒と回想の配置を設計する。回想は境界マークなし、自然な溶け込み（参照：`references/flashback-structure.md`）
3. 情報開示のタイミングを決める——読者は百合子視点で誠より先に真実を知り、誠視点で誠の誤解を追体験する。二層の劇的アイロニー（参照：`references/dramatic-irony.md`）
4. 各章の計画書を作成する

### Phase 4：執筆

1. **narrative-writer agent を spawn して本文を書かせる**
2. 写前準備：本章に関わるキャラ状態・封筒の進行段階・回想の有無・誠の文体段階を確認
3. **誠視点の章**では誠の一人称に徹する。内省を恐れず、自然な回想を溶け込ませる。**百合子視点の章**では百合子の一人称で過去の真実を開示する（参照：`references/first-person-tragedy.md`）
4. 書いた後：字数確認（5,000〜8,000字）・禁用語チェック・標点正規化・追跡更新
5. 参照：`references/banned-words.md`、スクリプト `scripts/normalize-punctuation.js`

### Phase 5：品質チェック

- 禁用語スキャン（万能比喩・章末総括は厳格に。心理フィルター語・会話タグは過剰使用のみ警告）
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
- `references/dramatic-irony.md` —— 劇的アイロニーの設計（1Q84型）
- `references/first-person-tragedy.md` —— 一人称悲劇と誠の文体段階
- `references/flashback-structure.md` —— 自然な回想の溶け込み
- `references/envelope-campaign.md` —— 破壊キャンペーンと情報分割開示

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
- `references/banned-words.md` —— 禁用語（村上文体対応版）

### 管理
- `references/state-tracking.md` —— キャラ状態追跡
- `references/outline-methods.md` —— 構成手法
- `references/cross-book-recall.md` —— 多巻連携
- `scripts/normalize-punctuation.js` —— 標点正規化

---

## 禁止事項

- 取引手法を具体的に開示しない（GoldenCross・移動平均線・デッドクロスの概念は登場させるが、具体的売買ロジックは書かない）
- 章末の総括・教訓・哲理を書かない（余韻——イメージ・情報の断片・静かな動作——で閉じる）
- 空虚な内省を書かない（「悲しかった」で終わらず、内省の過程を具体的に）
- 陳腐な万能比喩を使わない（「波のように」「稲妻のように」——日常的な具体的比喩は許容）
- 回想に境界マーク（`***`など）を使わない。自然に溶け込ませる
- 全キャラの口調を同一にしない（各キャラの7次元言語スタイルと character-voice ファイルに従う）
- 情報を一気に開示しない（封筒8通で分割開示）
