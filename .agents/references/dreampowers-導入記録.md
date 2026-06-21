# Dreampowers 導入記録

## 概要
Dreampowers（skyfiredao 作、GPL-3.0）は、opencode向け中国語小説執筆スキルセット（14スキル）。
フルインストールはせず、**中身の設計思想のみを抽出・翻訳**して既存ワークフローに組み込んだ。

## 導入決定の経緯

旧プロジェクト（51章）はスキルワークフローをバイパスした結果、キャラの声の統一・品質のばらつき・プロットの平面的さ・品質チェックのサボりという問題が発生した。

Dreampowers は以下の点で我々の問題に直接効く設計を持っていた：
- 7次元文体アンケート（dp-set-style）→ キャラの声の差別化
- 6アイアンルール（dp-set-outline）→ プロットの散漫防止・概念予算
- クレアモント係数 → 伏線債務の可視化
- 読者視点テスト（dp-review-reader）→ 品質チェックの充実

**乗り換えではなく「いいとこどり」** を選択した理由：
1. 我々は既に7体のカスタムエージェント（oh-story-claudecodeベース）を稼働させている
2. DreampowersはUnix向け（bashインストーラ・symlink）でWindowsに完全対応していない
3. 我々の38の参考ファイルはDreampowersにない独自資産
4. 4巻構成（FIRE/DeadCross/Breakout/LossCut）はDreampowersの単一作品想定に合わない

## 抽出した設計

| 抽出元 | ファイル名 | 設置先 | 使用タイミング |
|--------|-----------|--------|--------------|
| dp-set-style 7次元質問票 | `dreampowers-7dim-style.md` | `.agents/references/` | Phase 2（character-designer起動時） |
| dp-review-reader 4次元テスト | `dreampowers-reader-review.md` | `.agents/references/` | Phase 5（consistency-checker起動時） |
| dp-set-outline 6アイアンルール | story-outline.md の Rule 9-10 | `.agents/rules/` | Phase 3（計画作成時） |
| dp-set-outline クレアモント係数 | story-consistency.md の Rule 7 | `.agents/rules/` | Phase 5（品質チェック時） |

## 使い方

### Phase 2：character-designer 起動時
1. `.agents/references/dreampowers-7dim-style.md` を読み込む
2. 作品全体の文体を7次元アンケートで定義
3. 各キャラの7次元言語スタイルを個別に定義
4. 結果を `設定/キャラクター/*.md` に追記

### Phase 3：計画作成時
1. `.agents/rules/story-outline.md` の Rule 9（6アイアンルール）を遵守
2. 各章の新概念数をカウントし、概念予算内に収める
3. 五問ゲート（Rule 10）を各章計画に組み込む

### Phase 5：品質チェック時
1. `.agents/references/dreampowers-reader-review.md` の4次元評価を実行
2. consistency-checker が冷読みモードで各章を評価
3. `.agents/rules/story-consistency.md` の Rule 7（クレアモント係数）を計算
4. CC > 2 なら新規伏線を一時停止し回収を優先

## 利点と欠点

### 利点
- **ワークフロー不要で導入完了**: SKILL.mdの中身だけ読んで翻訳・保存しただけ。インストール不要
- **既存のルール・エージェントを強化**: 新しいシステムに乗り換えず、既存の資産を活かせる
- **日本語化済**: Dreampowersの中国語原文を日本語に翻訳し、プロジェクトの言語に統一
- **選択的適用**: 合わない設計は無理に取り入れない。我々に必要なものだけを抽出
- **軽量**: 追加ファイル3つ、編集2つ。リポジトリが膨らまない

### 欠点
- **強制力がない**: Dreampowers本来の「概念分離（物理ファイル隔離）」「プリドラフトゲート」「3段階レビューパイプライン」はファイルシステム＋ワークフロー構造のハード依存のため再現不可。ルールとして書いただけではバイパス可能
- **54人リファレンス作家未活用**: Dreampowersのdp-set-styleには54人+9ジャンルのスタイルリファレンスが含まれているが、中国網文＋欧米文学中心で日本のケータイ小説作家がいないため、現時点では導入していない。必要に応じて `.agents/references/dreampowers-作家リファレンス.md` として抽出可能
- **原文更新との同期**: Dreampowersリポジトリが更新された場合、翻訳版も追従する必要がある。現在は手動
- **原文の一部のみ抽出**: dp-set-outlineのテーマ織り込み・ナラティブタイムライン技法・POVルールなどは抽出していない。必要性が生じたら追加する

## 今後の拡張可能性

| 未抽出の設計 | 優先度 | 理由 |
|------------|--------|------|
| 54人+9ジャンル スタイルリファレンス | 低 | 日本のケータイ小説には直接適用できないが、参考にはなる |
| テーマ織り込み（テーマトラッキング） | 中 | 複数巻のテーマ一貫性に使える。Phase 3 で必要になったら抽出 |
| ナラティブタイムライン手法（順叙/倒叙/挿叙/補叙） | 中 | FIREのフラッシュバック構造の設計に直接使える |
| POVルール（視点切替5ルール） | 中 | 栞編・翼編は一人称。切替ルールが役立つ |
| リズムコントロール（2章高強度→1章緩衝） | 低 | 既存のAGENTS.mdでカバー済み |
