# 小説表紙ビジュアルスタイルライブラリ
各題材の網文表紙ビジュアルスタイル定義。GPT-Image-2 英語プロンプト構築に使用。

---

## プラットフォームスタイル

### 番茄小説

ビジュアル：高彩度・高コントラスト / 人物60%以上・顔鮮明 / 書名は太字大ゴシックで光彩効果(金/紅/白) / バストアップ構図+華麗背景
キーワード：`vibrant saturated colors, eye-catching bold design, character portrait dominating frame, mass-market novel cover style, high contrast`

### 起点

ビジュアル：繊細緻密でやや写実的イラスト / 構図にこだわり豊かなレイヤー / 書名は伝統的な毛筆楷書体 / 色彩は落ち着いた / 人物と背景のバランスが映画的
キーワード：`polished refined illustration, detailed cinematic composition, epic atmospheric, mature sophisticated style, premium quality`

### 晋江

ビジュアル：柔和な色調(ピンク/紫/水色/暖白) / 唯美な画風・大きな瞳・精巧な五官 / 花びら・光斑・シルク・宝飾装飾 / 中央対称で画面が清潔 / 書名は優雅な行書・細丸ゴシック
キーワード：`dreamy ethereal aesthetic, soft pastel tones, elegant romantic, delicate beauty, flower petals and bokeh`

### 知乎塩言

ビジュアル：余白たっぷりの極簡 / 冷めた色調(灰/青/白/暗色) / 雰囲気＞人物詳細、シーン/物品/抽象的イメージ多用 / 書名はモダンなサンセリフ / インディペンデント映画ポスター風
キーワード：`minimalist literary style, clean composition with negative space, subtle moody atmosphere, independent film poster aesthetic`

### 七猫

ビジュアル：極度に彩度が高く強いインパクト / 華麗な衣装・豊富な装備 / 炎・雷・霊力エフェクト / 書名は大きく発光・占有率大 / ポスター感・情報密度高
キーワード：`striking high-impact design, vivid dramatic colors, spectacular visual effects, attention-grabbing poster style`

### 刺猬猫

ビジュアル：日系イラスト・二次元 / 色彩明るく線画鮮明 / Q版要素 / 書名はカートゥーン手描き風 / 軽快で活発
キーワード：`anime illustration style, vibrant colorful, detailed character art, Japanese light novel aesthetic`

---

## 題材推定ルール

| キーワード | 題材 | スタイルタグ |
|:-------|:-----|:---------|
| 仙/道/剣/霊/修/宗/天/帝/尊/神 | 玄幻/仙侠 | xianxia fantasy |
| 都市/総裁/校園/重生/系統/学霸/医者/兵王 | 都市 | urban modern |
| 妃/皇/侯/宮/嫡/庶/后/朝/鳳/鸞 | 古言 | ancient romance |
| 総裁/契約/替嫁/甜寵/嬌妻/萌宝/閃婚 | 現言 | modern romance |
| 詭/案/探偵/懸疑/推理/密室/連続 | 懸疑 | mystery thriller |
| 星際/末世/機甲/賽博/廃土/進化 | 科幻 | sci-fi |
| 龍/騎/魔法/異世界/精霊/領主 | 西幻 | western fantasy |
| 三国/大明/大唐/戦場/将軍/謀士 | 歴史 | historical epic |
| 鬼/僵屍/陰陽/風水/盗墓/呪 | 霊異 | supernatural horror |
| 萌/喵/団寵/嬌/転生 | 軽小説 | light novel |

---

## プロンプト構築公式

```
[プラットフォームスタイル] + [文字層：書名＋著者名＋フォント設計] + [題材スタイルタグ] + [人物描写]
+ [背景要素] + [色彩指示] + [光彩指示] + [共通修飾]
```

共通修飾：`professional book cover design, high detail digital painting, portrait orientation 2:3 ratio, no watermark`

文字層は必ず指定：書名内容+位置(top center)+フォントスタイル+色；著者名内容+位置(bottom center)+フォントスタイル+色

---

## プロンプトテクニック

### 文字レンダリング

GPT-Image-2 は直接中国語をレンダリング可能。フォーマット：
```
Title text '書名' at top center in {フォントスタイル}
Author name '著者名' at bottom center in {フォントスタイル}
```

### 人物描写は具体的に

"a man"ではなく：
```
a young man in flowing white silk robes with gold embroidery,
long black hair tied in a topknot with a jade crown,
piercing dark eyes, confident expression,
holding a glowing blue spirit sword
```

### 背景三段構え

前景(人物/道具) / 中景(シーン：山頂/建築/森) / 遠景(雰囲気：雲海/星空/炎)

### 光彩効果

| 光彩 | キーワード | 印象 |
|------|--------|------|
| 神聖 | `dramatic golden light from above` | 神聖感 |
| 神秘的 | `cold moonlight from the left casting long shadows` | 神秘感 |
| 温かい | `warm sunset glow backlighting the figure` | 温かみ |
| 科幻 | `neon blue and purple lights from below` | SF感 |

### 写真風を避ける

`digital painting style` を追加。網文表紙にはイラスト感が必要。

### 構図バリエーション

| タイプ | キーワード | 用途 |
|:-----|:-------|:-----|
| 人物クローズアップ | `close-up portrait, face filling upper half` | キャラ強調 |
| 全身像 | `full body shot, dynamic pose` | 衣装・動作を展示 |
| 情景のみ | `no human figure, landscape composition` | 懸疑/科幻 |
| 双人 | `two figures facing each other` | 言情系 |

---

## スタイルライブラリ

### 玄幻 / 仙侠

**タグ**：`xianxia Chinese fantasy art style, ethereal atmosphere`
**色彩**：青藍+金+玄黒、寒色系基調、金色/暖色光源でアクセント
**人物**：男-長髪束ね/振り分け、剣/法器を携え、衣袂翻る / 女-仙裙でたなびき、霊獣同伴、蓮華飾り
**背景**：雲海、仙山、古建築楼閣、霊力光彩
**光彩**：`divine golden light rays, mystical mist, spiritual energy glow`
**例**：
```
Chinese web novel cover, xianxia fantasy style.
Title text '剑道独尊' at top center in bold golden brush calligraphy with metallic glow and sharp strokes.
Author name '青椒炒肉' at bottom center in small refined white serif text with faint golden glow, flanked by delicate cloud-scroll ornaments, resting on a thin horizontal gold line.
A young swordsman in flowing white robes standing on a mountain peak,
holding a glowing blue spirit sword, long black hair flowing in the wind.
Ethereal clouds swirling below, dramatic golden divine light from above,
spiritual energy particles. Dark misty mountain peaks in background.
Color palette: deep blue, gold, white, black.
Professional book cover, high detail digital painting, portrait 2:3 ratio, no watermark
```

### 都市

**タグ**：`modern urban contemporary style, clean cinematic composition`
**色彩**：深藍+灰+金、霓虹灯彩(夜景)/暖橙(夕暮れ)
**人物**：男-スーツ/カジュアル・シャープなシルエット / 女-ファッション着こなし・自信の表情
**背景**：都市スカイライン、高級オフィス、キャンパス、ネオンストリート
**光彩**：`sharp city lights, sunset glow reflecting on glass buildings, neon rim light`

### 古言 / 宮闘

**タグ**：`ancient Chinese romance palace drama, elegant classical beauty`
**色彩**：紅+金+墨黒、華やかで重厚
**人物**：女-華服盛装・鳳冠揺歩・精巧な化粧 / 男-帝王/将軍の威厳または温潤
**背景**：宫殿、庭園、紅牆、珠簾、屏風、提灯
**光彩**：`warm lantern light, golden candle glow, silk fabric shimmering`

### 現言 / 甜寵

**タグ**：`modern romance cover art, soft dreamy warm atmosphere`
**色彩**：ピンク+暖白+淡い金、暖かく柔らか
**人物**：双人構図主体、甘い交流(抱擁/見つめ合い/手つなぎ)
**背景**：カフェ、庭園、温かい室内、夕日ビーチ
**光彩**：`soft warm backlighting, dreamy bokeh, gentle sunset glow`

### 懸疑 / 推理

**タグ**：`dark mystery thriller, noir atmosphere, high contrast shadows`
**色彩**：黒+濃灰+暗青、血赤/冷白でアクセント
**人物**：シルエット/半顔隠れ/後ろ姿、冷静または緊張
**背景**：雨夜の街、老朽建築、密室、薄暗い路地
**光彩**：`dramatic chiaroscuro, single spotlight, rain-slicked reflections`

### 科幻 / 末世

**タグ**：`sci-fi cyberpunk, futuristic technology, post-apocalyptic`
**色彩**：深青+黒+銀、霓虹青/電子紫/エネルギー緑でアクセント
**人物**：機甲装/戦術服/ラボ服、SF武器/ホログラフィックUI
**背景**：宇宙、廃墟都市、実験室、宇宙ステーション
**光彩**：`holographic blue glow, neon rim lighting, energy arcs`

### 西幻

**タグ**：`western high fantasy, epic medieval atmosphere`
**色彩**：深青+鈍金+銀白、炎の赤/魔法紫でアクセント
**人物**：騎士鎧/魔法使いローブ/レンジャー革鎧、竜/グリフォン同伴
**背景**：城塞、竜の巣、魔法陣、広大な原野
**光彩**：`magic spell glow, dramatic stormy sky, firelight from torches`

### 歴史 / 軍事

**タグ**：`historical Chinese war epic, grand battlefield panorama`
**色彩**：鉄灰+暗紅+土黄、金鎧光沢/烽火橙でアクセント
**人物**：将軍鎧/謀士長袍、兵器携行
**背景**：戦場、城壁、軍営、狼煙
**光彩**：`dramatic battlefield firelight, smoke-filled sky, sunset over war`

### 霊異 / 恐怖

**タグ**：`Chinese supernatural horror, eerie ghostly atmosphere`
**色彩**：墨黒+幽緑+暗紅、紙白/灯明黄でアクセント
**人物**：道士装束/普通人が怪異に巻き込まれる、鬼影/紙人/僵屍
**背景**：墓地、古廟、薄暗い路地、棺桶
**光彩**：`eerie green glow, flickering candlelight, cold ghostly luminescence`

### 軽小説 / 二次元

**タグ**：`anime light novel cover, vibrant colorful moe style`
**色彩**：明るく多色使い、星/花びらで装飾
**人物**：Q版/萌系キャラ、猫耳/翼などの萌属性
**背景**：ファンタジー世界、学園、異世界、星空
**光彩**：`sparkly star effects, magical particle effects, soft luminous glow`
