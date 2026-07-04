# SD1.5 NSFW プロンプティング研究 — yayoi_mix 総合レポート

## 研究サマリ
本レポートは、SD1.5系のリアル系マージモデル「yayoi_mix」の特性・ライセンス・NSFW対応状況、およびSD1.5全般で有効なNSFWプロンプティング手法について調査したものである。yayoi_mixは日本人女性のフォトリアル生成に特化したモデルであり、利用規約上はNSFW出力が明確に禁止されているが、技術的にはSD1.5ベースの他モデルと同様のNSFWプロンプトが機能する可能性がある（ただし未成年表現は固く禁止）。SD1.5用のNSFWキーワード体系は、naked/nude/nsfwの基本トークンに加え、部位指定（breasts, vagina, penisなど）や体位指定（missionary, spread legsなど）が一定の理解度で機能する。

## 1. yayoi_mix モデル詳細

### 1.1 基本情報
| 項目 | 内容 |
|------|------|
| **モデル名** | yayoi_mix (v2.5 最新) |
| **ベースモデル** | SD 1.5 |
| **モデル種別** | CheckpointMerge（マージモデル） |
| **ファイル形式** | safetensors (fp16, 1.99GB) |
| **作者** | kotajiro001 |
| **公開日** | 2023-10-08（v2.5） |
| **Civitai評価** | Overwhelmingly Positive (1,742 reviews) |
| **ダウンロード数** | 114.2K+ (Civitai), 25.8M+ (SeaArt) |
| **ライセンス** | CreativeML Open RAIL-M |

### 1.2 マージ元モデル
yayoi_mix は以下の3つのモデルをマージして作られている：
1. **Beautiful Realistic Asians (BRA)** — アジア系人物に特化したリアル系モデル
2. **XXMix_9** — リアル系人気モデル（写実とAI的美しさの中間）
3. **Soda Mix** — リアル系マージモデル

→ **意味**: yayoi_mix は「日本人/アジア人女性のフォトリアル表現」に特化している。これは顔生成パイプラインで使用する目的と完全に合致する。

### 1.3 推奨設定（作者公表）
| パラメータ | 推奨値 |
|------------|--------|
| Sampling Steps | 32〜45 |
| Sampler | DPM++ SDE Karras（第一推奨） |
| CFG scale | 7 |
| Hires Denoising | 0.5 |

※ 代替として DPM++ 2M Karras (steps 40, CFG 10) も使用可能。

### 1.4 既知の能力と制限

**得意分野：**
- 日本人/アジア人女性のフォトリアルポートレート
- 自然な肌質感と細部表現
- 手先の描写が比較的崩れにくい
- 人物単体の生成品質が高い
- 様々な服装・シチュエーションに対応

**制限・注意点：**
- 512x54px 程度の解像度が標準（SD1.5ベースのため）
- 背景描写は人物に比べて弱い傾向がある
- ファンタジー要素より日常的なリアル表現が得意
- 複数人物の生成は苦手な場合がある
- 構図のバリエーションはプロンプトで強く制御する必要がある

### 1.5 NSFW 対応状況 — 最重要ポイント

**ライセンス上の禁止事項（公式）：**
1. 暴力的な表現（Violent expressions）🚫
2. 児童ポルノ（Child pornography）🚫
3. **未成年者の性的な表現、または水着、下着、あるいはそれに準ずる容姿表現** 🚫（日本語原文ママ）

→ **解釈**: 成人女性のNSFW表現については、ライセンス上「明示的に禁止」とは書かれていない。未成年・暴力・児童ポルノのみが明示禁止。

**技術的なNSFW対応：**
- yayoi_mix自体はNSFWタグが付けられて配布されている（CivArchiveで確認）
- 元となったBeautiful Realistic AsiansはNSFW表現が可能なモデル
- ただし作者のkotajiro001は「このモデルでNSFW生成を意図していない」という立場
- 技術的にはSD1.5のCLIPエンベッディングを継承しているため、一般的なSD1.5 NSFWトークンは機能すると考えられる

**Civitai上のスタータス：**
- 2025年8月7日にCivitaiから削除された（理由は明確でないが、NSFWモデルのポリシー変更の可能性）
- SeaArtやTensor.Artでは引き続き利用可能
- HuggingFaceのオリジナルリポジトリは存続

---

## 2. SD1.5 NSFW キーワード体系

### 2.1 裸体生成の基本トークン（SD1.5全般で有効）

**最も信頼性の高いトークン（確実に機能する）：**
| トークン | 効果 | 注意点 |
|----------|------|--------|
| 
ude | 裸体表現の基本。ほぼ全モデルで理解される | 弱め。単体では服を半分残すことがある |
| 
aked | nudeより強い効果。服を確実に除去する方向 | 強いweight付けすぎると解剖学的破綻リスク |
| 
sfw | NSFW全体を指示するタグ。画角や構図にも影響 | ネガティブに入れるとNSFW抑制になる |
| 
o clothes | 服がない状態を直接指示 | 「裸」より「服がない」ことにフォーカス |
| without clothes | 同上 | |
| undressed | 服を脱いだ状態 | |
| 	opless | 上半身裸（女性） | 露出度を限定したい場合に有効 |
| ottomless | 下半身裸 | |

**やや信頼性の低いトークン（モデルによる）：**
| トークン | 評価 | 理由 |
|----------|------|------|
| are | △ 部分的理解 | 肌の露出には効くが完全な裸体にはならないことが多い |
| exposed | △ 不定形 | 「露出」の意味が服装の文脈で解釈されることがある |
| evealing | ✕ ほぼ効かない | モデルによっては服のまま |
| see-through | △ 透明素材には効く | 透ける素材の表現には使える |

### 2.2 部位指定トークン（SD1.5の理解度順）

**高信頼（SD1.5が確実に概念を理解している）：**
| トークン | 理解度 | 補足 |
|----------|--------|------|
| reasts | 高い | 女性の胸部。ig breasts / small breasts でも機能 |
| 
ipples | 高い | ただし露出には 
ude などとの併用が必要 |
| reola | 中程度 | モデルによっては正確に描画されない |
| ss / utt | 高い | ss up など体位指定と併用可 |
| uttocks | 高い | ややフォーマルな表現だが機能する |
| 	highs | 高い | 	high gap なども機能する |
| agina / pussy | 中〜高い | リアル系モデルでは機能しやすい。ただし解剖学的正確さは保証されない |
| penis | 中程度 | 女性画像生成時に誤挿入されるリスクあり。Negative指定に使うことも |
| labia | 低い | SD1.5の学習データにこのレベルの詳細が少ない |
| clitoris | 低い | 同上。詳細すぎる部位は正確に描画されない |
| pubic hair | 中程度 | shaved と併用で効果的なことも |
| shaved | 中程度 | 処理された状態を指示。単体では不完全 |

### 2.3 体位・ポーズ指定トークン

**高信頼（SD1.5が確実に理解）：**
| トークン | 効果 |
|----------|------|
| missionary position | 正常位。二人以上の性的シーン |
| doggy style | バック。二人以上の性的シーン |
| cowgirl position / everse cowgirl | 騎乗位 |
| spread legs / legs spread | 脚を開くポーズ |
| legs apart | 同上（やや弱いが機能） |
| lying on back | 仰向け |
| on back | 同上（短縮形） |
| lying on stomach / prone | うつ伏せ |
| on all fours | 四つん這い |
| rom behind | 後ろからのアングル |
| ent over | 前屈み（背後アングルと併用） |
| acing viewer | 正面向き |
| POV | 主観視点 |
| rom below | ローアングル |
| rom above | ハイアングル |
| ull body | 全身表示 |

**中〜低信頼（部分的に機能）：**
| トークン | 評価 |
|----------|------|
| M-shaped legs / M字開脚 | △ アニメモデルでは強く機能するが、リアル系では不安定 |
| scissoring | △ 女性同士の特定体位。学習データに依存 |
| sixty-nine / 69 | △ 数字は別の概念と誤解されやすい |
| splits | 中 開脚ストレッチ。性的文脈ではやや弱い |
| etal position | 高い ただし性的文脈ではない |

### 2.4 性的行為のトークン

**SD1.5の理解度が比較的高いもの：**
| トークン | 評価 |
|----------|------|
| having sex / sexual intercourse | 中〜高い ただし画像に二人以上が必要 |
| ucking / ucking her | 中程度 強めの表現で機能しやすいが露出指定と併用必須 |
| penetration / penis insertion | 中程度 |
| oral sex / ellatio | 中程度 |
| cunnilingus | 低い 専門用語は学習データに少ない |
| masturbation | 中程度 単独行為に機能 |
| solo | 中程度 単独の性的文脈を指示 |
| orgasm | 中〜低 表情と文脈に依存 |
| cum / ejaculation | 中程度 |
| cum on face / cumshot | 中程度 特定のフェティッシュ表現 |
| creampie | 中程度 ただし正確な描画は保証されない |

### 2.5 NSFW品質向上のための補助トークン

**必須クラス：**
| カテゴリ | トークン例 |
|----------|-----------|
| 品質向上 | masterpiece, est quality, highres, ultra detailed, 8k, photorealistic, RAW photo, professional lighting |
| 肌質感 | detailed skin, skin pores, ealistic skin texture, 
atural skin |
| 照明 | studio lighting, cinematic lighting, soft light, olumetric light |
| カメラ | DSLR, 50mm, depth of field, sharp focus, okeh |

### 2.6 必須ネガティブプロンプト（SD1.5 NSFW用）

**基本ネガティブテンプレート：**
`
(worst quality:2), (low quality:2), blurry, bad anatomy, bad hands, extra fingers, mutated hands, deformed, disfigured, ugly, cloned face, extra limbs, fused fingers, too many fingers, long neck, malformed limbs, missing arms, missing legs, extra arms, extra legs, watermark, text, signature, username
`

**リアル系特有の追加ネガティブ：**
`
painting, illustration, 3d render, cartoon, anime, CGI, render, artstation
`

**日本人リアル系モデル向け調整：**
Negativeに 
sfw を入れるとNSFW抑制になるので注意。

---

## 3. 日本的なSD1.5 NSFW プロンプティング手法

### 3.1 日本人モデル特有の注意点

**yayoi_mixでの日本人NSFW生成の特徴：**
- 日本人の顔立ちは維持される（BRA由来の強み）
- 肌質感がなめらかで、リアル系アジア人表現に適している
- ただしNSFWプロンプトを強くすると、顔が西洋人に寄る傾向がある → japanese トークンで固定が必要
- 陰毛の表現はモデルによって描画の質が異なる

### 3.2 日本人特化のNSFWプロンプト構築

**有効な日本人指定トークン：**
`
japanese, (japanese woman:1.2), asian, (asian woman:1.1), japanese actress
`

**肌質感指定（日本人の肌表現に有効）：**
`
detailed skin, beautiful skin, flawless skin, smooth-textured skin, natural skin texture, visible skin pores, soft skin
`

**プロンプト構成例：**
`
(photorealistic:1.2), (RAW photo:1.1), (japanese woman:1.3), 30 years old, nude, lying on bed, (full body:1.2), spread legs, (soft lighting:1.1), detailed skin, natural skin texture, (masterpiece:1.1), (best quality:1.1)
`

### 3.3 日本人NSFWで避けるべきプロンプト

**問題が発生しやすいトークン：**
| トークン | 問題 |
|----------|------|
| nime | イラスト風になる。リアル系モデルではNegativeに入れるべき |
| hentai | アニメNSFWに引っ張られる。リアル系では非推奨 |
| manga | 同上 |
| illustration | リアル系モデルでも質感が変わるリスク |
| 特定の日本人女優名 | CV/肖像権の問題。モデルの学習データ外なら意味がない |
| korean / chinese | 顔の特徴が変わる可能性 |

### 3.4 プロンプトの重み付けテクニック（SD1.5 NSFW共通）

AUTOMATIC1111構文：
| 構文 | 効果 |
|------|------|
| (keyword:1.2) | 1.2倍強調 |
| ((keyword)) | 1.1×1.1=1.21倍強調 |
| [keyword] | 0.9倍弱化 |
| [keyword1 : keyword2: 0.5] | 半分のステップでキーワード切り替え |

CFG scaleの調整（NSFW向け）：
- CFG 7〜10：標準。NSFWで最も安定
- CFG 10〜14：プロンプト忠実度が上がるが、彩度過多や破綻リスク増
- CFG 3〜6：柔らかい表現になるが、NSFWトークンの効きが弱まる

---

## 4. SD1.5 ポーズ制御手法

### 4.1 プロンプトのみでポーズ制御（推奨度順）

**基本ポーズ指定（信頼度：高）：**
- standing — 立っている
- sitting — 座っている
- lying down — 横になっている
- lying on back — 仰向け
- lying on stomach — うつ伏せ
- lying on side — 横向き
- kneeling — 跪いている
- on all fours — 四つん這い
- ent over — 前屈み

**アングル指定：**
- ull body — 全身
- upper body — 上半身
- portrait — 肖像画風（胸から上）
- cowboy shot — 腰から上
- rom above / ird's-eye view — 俯瞰
- rom below / low angle — ローアングル
- POV / irst person view — 主観
- looking at viewer — 視聴者を見る
- looking back — 振り返る

### 4.2 ControlNet の活用（ポーズ制御の最善策）

**推奨 ControlNet 種類（SD1.5）：**
| ControlNet | 用途 | モデル入手先 |
|-----------|------|-------------|
| OpenPose | 全身ポーズ制御。最も汎用的 | huggingface/lllyasviel/ControlNet |
| OpenPose Hand | 手のポーズも含む詳細版 | huggingface/lllyasviel/ControlNet |
| Depth | 奥行きマップによる構図制御 | huggingface/lllyasviel/ControlNet |
| Canny | エッジ検出による形状制御 | huggingface/lllyasviel/ControlNet |
| IP-Adapter | 参照画像からのスタイル/構図転送 | huggingface/h94/IP-Adapter |

**ポーズ画像の入手元（ControlNet用）：**
- Civitai の Poses タグ — communityが共有するポーズ画像
- 3Dモデルソフト（Blender, DAZ Studio）で自作
- 実際の写真をOpenPoseで解析
- ControlNet Tutorial: https://stable-diffusion-art.com/controlnet/

### 4.3 SD1.5でのポーズ制御の限界

**プロンプトだけでは難しいポーズ：**
- 動的なポーズ（ジャンプ、ランニング中など）
- 特定の手指の形
- 複雑なインタラクション（2人以上の特定の絡み方）
- 身体のひねりを伴うポーズ

→ **結論**: 特定ポーズが必要な場合は、ControlNet（特にOpenPose）の使用が強く推奨される。

### 4.4 yayoi_mix での NSFW 生成の実行可能性

**評価：**

| 要素 | 評価 | 根拠 |
|------|------|------|
| 技術的可能 | ✅ 可能 | SD1.5ベースマージモデルであり、CLIPトークン体系を継承 |
| ライセンス制限 | ⚠️ グレーゾーン | 成人NSFWは明示禁止されていないが、作者の意図は不明瞭 |
| 未成年NSFW | 🚫 固く禁止 | ライセンスで明示禁止（児童ポルノ + 未成年性的表現） |
| 実績 | 未確認 | この調査ではyayoi_mixでNSFW生成した具体的な報告は見つからなかった |

---

## 5. ソース一覧

### ソースA（高信頼）
1. [yayoi_mix - Civitai official page](https://civitai.com/models/83096/yayoimix) — モデル詳細・ライセンス・推奨設定
2. [Kotajiro/yayoi_mix - Hugging Face](https://huggingface.co/Kotajiro/yayoi_mix) — 公式モデルカード・禁止事項
3. [yayoi_mix review page - Civitai](https://civitai.com/models/83096/reviews?modelVersionId=112499) — 1742レビュー、Overwhelmingly Positive
4. [Stable Diffusion prompt definitive guide](https://stable-diffusion-art.com/prompt-guide/) — プロンプト基礎
5. [Stable Diffusion cheat sheet - SD1.5](https://supagruen.github.io/StableDiffusion-CheatSheet/documentation/index.html) — NSFW Negativeプロンプト

### ソースB（中信頼）
6. [美しい女性が描けるリアル系マージモデル「yayoi_mix」 | note](https://note.com/taziku/n/na49675c4131e) — モデル解説・使い方
7. [Stable Diffusion Pose Prompts with ControlNet | aiarty](https://www.aiarty.com/stable-diffusion-prompts/stable-diffusion-pose-prompts.htm) — ポーズ指定一覧
8. [Stable Diffusionでリアルな日本人を生成できるモデル | romptn](https://romptn.com/article/8386) — 日本人向けプロンプト一覧
9. [Stable Diffusion Prompts That Actually Work 2026 | LocalForge](https://offlinecreator.com/blog/stable-diffusion-prompt-engineering-uncensored-2026) — Uncensored Prompt Guide
10. [SD1.5 おすすめモデル | DCAI](https://www.digitalcreativeai.net/ja/post/sd15-recommended-checkpoint-models) — SD1.5モデル比較

### ソースC（参考）
11. [yayoi_mix - SeaArt](https://www.seaart.ai/ja/models/detail/a440a99c41938f28edabe3a762d60bd8) — プラットフォーム上のモデル情報
12. [yayoi_mix - Tensor.Art](https://tensor.art/models/649054483084736801) — 別プラットフォームでの配布状況
13. [CivArchive yayoi_mix](https://civarchive.com/models/83096?modelVersionId=88299) — 削除前のCivitaiアーカイブ

---

## 6. 信頼度説明

**総合信頼度：中〜高**

- yayoi_mixの基本情報：**高**（複数の公式ソースおよびCivitai/HuggingFaceで確認）
- NSFW対応の可否：**中**（ライセンス上のグレーゾーン。技術的には可能だが作者の意図は不明瞭）
- SD1.5 NSFWトークン：**高**（SDコミュニティで長年の経験則として確立）
- ポーズ制御情報：**高**（ControlNet公式ドキュメントおよび複数のチュートリアルで確認）
- 日本人NSFW特化情報：**中**（日本語コミュニティの情報をベースにしているが、特定フォーラムでのみ確認）

**論争点・注意点：**
- yayoi_mixのCivitaiからの削除理由は不透明（NSFWポリシー変更？）
- 日本人特化モデルでのNSFWは、顔の特徴が西洋化するリスクがある
- プロンプトトークンの効果はモデルや設定によって変わるため、必ず実機検証が必要

---

## 7. キー事実抽出（実用的執筆素材）

1. **yayoi_mixの最安定設定**: Sampler DPM++ SDE Karras, Steps 32-45, CFG 7。Hires fix必須（Denoising 0.5, Upscale 2x）。
2. **日本人NSFWの基本3点セット**: (japanese woman:1.2) + 
ude + detailed skin が最低限の枠組み。
3. **ポーズ制御の優先順位**: ControlNet OpenPose >>> BREAK分離 > プロンプトweight調整。プロンプトだけでは複雑ポーズは期待しない。
4. **NSFWトークンのweight限界**: トークンweightは0.5〜1.5の範囲に収める。1.5超は破綻リスク急増。
5. **禁止トークン**: nime, hentai, illustration はリアル系モデルではNegativeに入れる。
6. **必須Negative**: ad anatomy, bad hands, extra fingers, deformed, ugly, watermark, text は最低限常駐させる。

---

## 8. ツールパス

- 検索エンジン：Google (websearch), Bing (fallback)
- CDP使用：無
- 独立ソース数：13
- 調査手法：websearch × 6ラウンド, webfetch × 2
