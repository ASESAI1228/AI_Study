# API連携の基礎

## APIとは

- Application Programming Interface（アプリケーション・プログラミング・インターフェース）
- ソフトウェア同士が通信するための仕組み
- AIサービスの機能を外部から利用するための標準的な方法
- HTTP/HTTPSプロトコルを使用したRESTful APIが一般的

## 主要なAI APIの概要

### OpenAI API
- **提供機能**: GPT-4, GPT-3.5-Turbo, DALL-E, Whisperなど
- **特徴**: 高性能な言語モデル、画像生成、音声認識
- **料金体系**: トークン単位の従量課金制
- **ドキュメント**: [OpenAI API Documentation](https://platform.openai.com/docs/)

### Google Cloud AI API
- **提供機能**: Gemini API, Vertex AI, Speech-to-Text, Translationなど
- **特徴**: Googleの検索技術との統合、多言語対応
- **料金体系**: 使用量ベースの従量課金制
- **ドキュメント**: [Google Cloud AI Documentation](https://cloud.google.com/ai-platform/docs)

### Anthropic Claude API
- **提供機能**: Claude 3 Opus, Sonnet, Haikuなど
- **特徴**: 長文処理、安全性重視
- **料金体系**: トークン単位の従量課金制
- **ドキュメント**: [Anthropic API Documentation](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)

## API連携の基本概念

### APIキー
- APIへのアクセス権を管理する認証情報
- 秘密情報として安全に管理する必要がある
- 環境変数や設定ファイルで管理するベストプラクティス

### エンドポイント
- APIにアクセスするためのURL
- 機能ごとに異なるエンドポイントが提供される
- 例: `https://api.openai.com/v1/chat/completions`

### リクエストとレスポンス
- **リクエスト**: クライアントからAPIへの要求
  - HTTPメソッド（GET, POST, PUT, DELETEなど）
  - ヘッダー（認証情報、コンテンツタイプなど）
  - ボディ（JSONデータなど）
- **レスポンス**: APIからクライアントへの応答
  - ステータスコード（200, 400, 500など）
  - レスポンスボディ（JSONデータなど）

### レート制限
- APIの過剰利用を防ぐための制限
- 時間あたりのリクエスト数や同時接続数の制限
- 制限超過時の対応（バックオフ、リトライなど）

## OpenAI APIの基本的な使い方

### APIキーの取得と管理
1. OpenAIアカウントの作成
2. APIキーの発行（[OpenAI Platform](https://platform.openai.com/)）
3. APIキーの安全な管理（環境変数など）

### 基本的なリクエスト構造
```python
import openai

# APIキーの設定
openai.api_key = "your-api-key"

# GPT-3.5-Turboへのリクエスト
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "あなたは法務アシスタントです。"},
        {"role": "user", "content": "契約書の重要条項について教えてください。"}
    ],
    temperature=0.7,
    max_tokens=500
)

# レスポンスの処理
print(response.choices[0].message.content)
```

### 主要なパラメータ
- **model**: 使用するモデル（"gpt-4", "gpt-3.5-turbo"など）
- **messages**: 会話履歴（system, user, assistantのロール）
- **temperature**: 出力のランダム性（0.0〜2.0）
- **max_tokens**: 最大出力トークン数
- **top_p**: 確率分布のカットオフ（核サンプリング）
- **frequency_penalty**: 単語の繰り返しを減らす（-2.0〜2.0）
- **presence_penalty**: 新しいトピックの導入を促進（-2.0〜2.0）

## Claude APIの基本的な使い方

### APIキーの取得と管理
1. Anthropicアカウントの作成
2. APIキーの発行（[Anthropic Console](https://console.anthropic.com/)）
3. APIキーの安全な管理

### 基本的なリクエスト構造
```python
import anthropic

# クライアントの初期化
client = anthropic.Anthropic(api_key="your-api-key")

# Claudeへのリクエスト
message = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1000,
    temperature=0.7,
    system="あなたは法務アシスタントです。法的な質問に正確に回答してください。",
    messages=[
        {"role": "user", "content": "契約書の重要条項について教えてください。"}
    ]
)

# レスポンスの処理
print(message.content)
```

## エラーハンドリングとベストプラクティス

### 一般的なエラーと対処法
- **認証エラー**: APIキーの確認
- **レート制限**: バックオフとリトライ
- **無効なリクエスト**: パラメータの確認
- **サーバーエラー**: 一時的な問題の場合はリトライ

### エラーハンドリングの実装例
```python
import openai
import time
from openai import OpenAIError

def call_openai_with_retry(max_retries=3, backoff_factor=2):
    retries = 0
    while retries < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "こんにちは"}],
                max_tokens=100
            )
            return response
        except OpenAIError as e:
            retries += 1
            if retries >= max_retries:
                raise e
            sleep_time = backoff_factor ** retries
            print(f"エラー発生: {e}. {sleep_time}秒後にリトライします。")
            time.sleep(sleep_time)
```

### APIキーのセキュリティ
- 環境変数での管理
- バージョン管理システムへの登録禁止
- 定期的なキーのローテーション
- 最小権限の原則（必要最小限の権限付与）

### コスト管理
- 使用量のモニタリング
- 予算上限の設定
- トークン数の最適化
- キャッシュの活用

## 法務分野でのAPI活用例

### 契約書分析システム
```python
def analyze_contract(contract_text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたは契約書分析の専門家です。"},
            {"role": "user", "content": f"以下の契約書を分析し、重要条項、リスク、改善点を抽出してください:\n\n{contract_text}"}
        ],
        temperature=0.2,
        max_tokens=1000
    )
    return response.choices[0].message.content
```

### 法的質問応答システム
```python
def legal_qa_system(question):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたは日本の法律に詳しい法務アシスタントです。"},
            {"role": "user", "content": question}
        ],
        temperature=0.3,
        max_tokens=800
    )
    return response.choices[0].message.content
```

### 文書要約システム
```python
def summarize_legal_document(document_text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "法的文書を簡潔に要約してください。"},
            {"role": "user", "content": document_text}
        ],
        temperature=0.3,
        max_tokens=500
    )
    return response.choices[0].message.content
```

## 次回予告：法的文書分析の実践

- 契約書の自動分析手法
- 判例文書からの情報抽出
- 法的文書の要約と分類
- 実務での活用事例 