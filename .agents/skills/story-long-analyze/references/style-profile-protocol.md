# 文体プロファイルプロトコル

`story-long-analyze` と `style-profile-generator.md` 間のデータ交換プロトコル。

## プロトコル概要

- フォーマット：JSON（`.json` ファイル）
- エンコーディング：UTF-8
- 生成元：`style-profile-generator.md` に従い、story-architect agent が走査範囲の全作品から生成
- 使用方法：`story-long-analyze` の文体プロファイル生成フェーズで reader agent が直接呼び出し
- ファイル命名規則：`文体プロファイル_{作品名}.json`
- 格納先：`{作品}/参照/{作品名}/文体プロファイル_{作品名}.json`

## トップレベル構造

```json
{
  "profile": {
    "title": "完全な作品名",
    "author": "著者名（なくても可）",
    "source": "データソースの説明（オリジナル/Web/ユーザーアップロード/データベース等）",
    "generatedAt": "ISO 8601 タイムスタンプ",
    "analysisScope": "分析範囲の説明、例：黄金三章（第1〜3章）全文分析 or 全 30 章精読分析"
  },
  "styleAnalysis": {},
  "rhetoricAnalysis": {},
  "emotionalRhythm": {},
  "hookTechniques": {},
  "readerFeedback": {},
  "marketMetrics": {}
}
```

## 各モジュールの詳細定義

### 文体分析（styleAnalysis）

```json
{
  "styleAnalysis": {
    "narrativePerspective": "叙述視点の説明",
    "sentenceStyle": "句長分布・リズム分析の説明",
    "descriptionDensity": "描写密度（対話・心理・環境描写の比率概算）",
    "dialogueStyle": "対話形式の特徴（地の文付き/独立行/タグの使用等）",
    "paragraphStructure": "段落構造の特徴（短文多段/長文少段等）",
    "overallStyle": "全体的な文体印象"
  }
}
```

### 修辞分析（rhetoricAnalysis）

```json
{
  "rhetoricAnalysis": {
    "figuresOfSpeech": ["修辞技法リスト、例：比喩、擬人、排比"],
    "frequency": "修辞技法の使用頻度評価（多/中/少）",
    "typicalExamples": [
      {
        "technique": "技法名",
        "example": "原文例文",
        "effect": "読者への影響説明"
      }
    ]
  }
}
```

### 感情リズム分析（emotionalRhythm）

```json
{
  "emotionalRhythm": {
    "overallEmotionalCurve": "感情曲線の全体的な説明",
    "peakCount": "感情のピーク出現回数",
    "peakDistribution": "ピーク位置の分布説明",
    "tensionReleasePattern": "張弛リズムの説明",
    "typicalWave": [
      {
        "range": "章範囲（例：第1〜3章）",
        "dominantEmotion": "主感情",
        "intensity": "感情強度（1-10）",
        "description": "このウェーブの説明"
      }
    ]
  }
}
```

### フック技法分析（hookTechniques）

```json
{
  "hookTechniques": {
    "chapterEndHookType": ["章末フックタイプリスト"],
    "chapterStartHookType": ["章頭フックタイプリスト"],
    "typicalExample": [
      {
        "hookType": "フックタイプ",
        "chapter": "所在章",
        "example": "フック原文",
        "effectAnalysis": "効果分析"
      }
    ],
    "hookDensity": "フック密度（平均何段落または何文字ごとに1回のフック）"
  }
}
```

### 読者反応分析（readerFeedback）

> 省略可能モジュール。読者コメント/データがあれば記入。

```json
{
  "readerFeedback": {
    "dataSource": "データソースの説明（例：Web クローリング、プラットフォーム表示データ、無）",
    "overallRating": "総合評価（データなしは null）",
    "commentHighFreq": ["高頻度コメントキーワード"],
    "representativeComment": [
      {
        "commentType": "コメントタイプ（肯定/批判/提案）",
        "content": "コメント内容",
        "likeCount": "いいね数"
      }
    ]
  }
}
```

### 市場指標分析（marketMetrics）

> 省略可能モジュール。市場データがあれば記入。

```json
{
  "marketMetrics": {
    "dataSource": "データソースの説明",
    "rankings": "ランキングデータ",
    "estimatedReaders": "推定読者数（null 可）",
    "estimatedRevenue": "推定収入（null 可）"
  }
}
```

## プロトコル遵守の制約

- 未入手のデータフィールドは削除せず、`null` 値で出力する
- 文体プロファイルを保存する際は必ず JSON フォーマットを検証する（`json` がパース可能かチェック）
- 同じ作品に対して：生成された文体プロファイルを一度だけ保存し、内容変更が必要な場合のみ新しいバージョンで上書きする
- ファイル名には特殊記号を含めず、スペースは `_` に置き換える
