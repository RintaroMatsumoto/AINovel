# スキャンデータ収集フォーマット仕様
起点/番茄/七猫/晋江の収集フィールド、出力テンプレート、クレンジングルールを定義。

---

## 起点

### 起点収集説明

優先的に `scripts/qidian-rank-scraper.js` のデフォルト `--mode auto` を使用。スクリプトはまず `https://m.qidian.com` モバイル端末 SSR pageContext JSON を読み取り、PC 站の風コントロールページを回避。モバイル端末が利用不可の場合のみ CDP/PC ページにフォールバック。出力ヘッダーには `取得方式：mobile-ssr` または `cdp-pc` と記載。

### ランキングURL

| ランキング | URL |
|------|-----|
| 新人契約新書榜 | qidian.com/rank/newsign/ |
| 契約作者新書榜 | qidian.com/rank/signnewbook/ |
| 一般作者新書榜 | qidian.com/rank/pubnewbook/ |
| 新人作者新書榜 | qidian.com/rank/newauthor/ |
| 三江推薦 | qidian.com/sanjiang/（非 /rank/ パス、週ごとにグループ化） |
| 月票榜 | qidian.com/rank/yuepiao/ |
| 暢銷榜 | qidian.com/rank/hotsales/ |
| 読書指数榜 | qidian.com/rank/readindex/ |
| 收藏榜 | qidian.com/rank/collect/ |
| 原創推薦榜 | qidian.com/rank/recom/ |

### フィールド

順位 | 書名 | 著者 | 題材 | 状態 | 契約 | 課金モード | 文字数（万字） | 総推薦 | タグ（詳細ページ） | 最終更新（詳細ページ） | 作品ページリンク | 紹介（詳細ページ、100字で切捨て）

---

## 番茄

### ランキングURL

### フィールド

---

## 七猫

### ランキングURL

### フィールド

---

## 晋江

### ランキングURL

### フィールド
