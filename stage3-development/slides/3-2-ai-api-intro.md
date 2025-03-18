# AI API入門

## AI APIとは

- AIの機能をプログラムから利用するための仕組み
- HTTPリクエストを通じてAIモデルにアクセス
- 認証キーを使用してセキュアに通信
- 様々なAI機能（テキスト生成、画像生成、音声認識など）を利用可能

## 主要なAI API提供企業

- OpenAI（GPTモデル）
- Google（Gemini API）
- Anthropic（Claude API）
- その他（Cohere, Mistral AI, Stability AI など）

## API利用のメリット

- 自社サービスにAI機能を組み込める
- ローカル環境での重いモデル実行が不要
- 常に最新のモデルにアクセス可能
- スケーラブルな処理が可能

## API利用の基本的な流れ

【python】
# 1. 必要なライブラリのインポート
import requests
import json

# 2. APIキーの設定
api_key = "your_api_key_here"

# 3. リクエストヘッダーの設定
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# 4. リクエストボディの作成
data = {
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "system", "content": "あなたは法務アシスタントです。"},
        {"role": "user", "content": "契約書のレビューポイントを教えてください。"}
    ]
}

# 5. APIリクエストの送信
response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers=headers,
    json=data
)

# 6. レスポンスの処理
if response.status_code == 200:
    result = response.json()
    print(result["choices"][0]["message"]["content"])
else:
    print(f"エラー: {response.status_code}")
    print(response.text)
【python】

## OpenAI API

### 概要
- GPT-3.5, GPT-4などの強力な言語モデルを提供
- テキスト生成、チャット、埋め込み、画像生成など多様な機能
- 従量課金制（トークン数に基づく）

### 主な機能
- Chat Completions API（チャット形式の対話）
- Completions API（テキスト生成）
- Embeddings API（テキストの数値ベクトル化）
- DALL-E API（画像生成）
- Whisper API（音声認識）

### 認証と設定
- APIキーの取得: [OpenAIダッシュボード](https://platform.openai.com/)
- 利用制限の設定
- 支払い方法の登録

## Google AI (Gemini) API

### 概要
- Googleの最新AI技術を提供
- Gemini（旧PaLM）モデルへのアクセス
- マルチモーダル機能（テキスト、画像、音声）

### 主な機能
- テキスト生成
- チャット対話
- 埋め込みベクトル生成
- 画像理解と生成

### 認証と設定
- Google Cloud Platformでのプロジェクト作成
- APIキーの取得
- 利用量の監視とクォータ設定

## Anthropic Claude API

### 概要
- 安全性と倫理性を重視したAIモデル
- 長いコンテキスト処理が可能（Claude 3 Opusは最大200K tokens）
- 自然な対話と詳細な説明が得意

### 主な機能
- テキスト生成
- 対話型応答
- 文書分析と要約
- コード生成と説明

### 認証と設定
- Anthropicコンソールでのアカウント作成
- APIキーの取得
- 利用制限の確認

## API利用時の注意点

### セキュリティ
- APIキーの安全な管理（環境変数の利用）
- 機密情報の送信に注意
- レート制限の考慮

### コスト管理
- 利用量の監視
- 予算上限の設定
- 効率的なプロンプト設計

### プライバシーとコンプライアンス
- 個人情報の取り扱い
- データの保持ポリシーの確認
- 各国の規制への対応

## 次回予告：OpenAI API実践

- OpenAI APIの詳細設定
- 効果的なプロンプト設計
- エラーハンドリングとリトライ
- ストリーミングレスポンスの活用 