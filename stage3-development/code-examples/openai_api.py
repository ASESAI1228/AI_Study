# OpenAI API 利用サンプル

# 必要なライブラリのインストール
# pip install openai

import openai
import os
import json
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む（APIキーを安全に管理するため）
load_dotenv()

# APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# モデル一覧を取得する関数
def list_models():
    try:
        models = openai.Model.list()
        print("利用可能なモデル:")
        for model in models["data"]:
            print(f"- {model['id']}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# チャット形式でAIと対話する関数
def chat_with_ai(system_prompt, user_prompt, model="gpt-3.5-turbo"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,  # 創造性の度合い（0.0〜1.0）
            max_tokens=1000,  # 最大トークン数
            top_p=1.0,        # 出力の多様性
            frequency_penalty=0.0,  # 単語の繰り返しにペナルティ
            presence_penalty=0.0    # 新しいトピックの導入を促進
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"エラーが発生しました: {e}"

# テキストの埋め込みベクトルを取得する関数
def get_embedding(text, model="text-embedding-ada-002"):
    try:
        response = openai.Embedding.create(
            model=model,
            input=text
        )
        embedding = response["data"][0]["embedding"]
        return embedding
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# DALL-Eを使用して画像を生成する関数
def generate_image(prompt, size="1024x1024", n=1):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=n,
            size=size
        )
        return response["data"][0]["url"]
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# ストリーミングレスポンスを使用したチャット関数
def chat_with_streaming(system_prompt, user_prompt, model="gpt-3.5-turbo"):
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            stream=True  # ストリーミングを有効化
        )
        
        # ストリーミングレスポンスを処理
        collected_chunks = []
        collected_messages = []
        
        print("AIの回答（ストリーミング）:")
        for chunk in response:
            collected_chunks.append(chunk)
            chunk_message = chunk["choices"][0]["delta"]
            collected_messages.append(chunk_message)
            
            if "content" in chunk_message:
                print(chunk_message["content"], end="", flush=True)
        
        print("\n")
        return collected_messages
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# 法務関連のプロンプト例
legal_system_prompt = """
あなたは経験豊富な法務アシスタントです。
契約書のレビューや法的アドバイスを提供します。
専門用語を適切に使いながらも、わかりやすく説明してください。
日本の法律に基づいた回答を心がけてください。
"""

# メイン処理
if __name__ == "__main__":
    print("OpenAI APIサンプルプログラム\n")
    
    # 利用可能なモデルを表示
    list_models()
    
    print("\n=== チャットサンプル ===")
    user_question = "秘密保持契約（NDA）の主要な条項について教えてください。"
    response = chat_with_ai(legal_system_prompt, user_question)
    print(f"質問: {user_question}")
    print(f"回答: {response}\n")
    
    print("=== 埋め込みベクトルサンプル ===")
    text_to_embed = "この契約は、甲と乙の間で締結される秘密保持契約である。"
    embedding = get_embedding(text_to_embed)
    if embedding:
        print(f"テキスト「{text_to_embed}」の埋め込みベクトル（最初の5要素）:")
        print(embedding[:5])
        print(f"ベクトルの次元数: {len(embedding)}\n")
    
    print("=== 画像生成サンプル ===")
    image_prompt = "A professional lawyer reviewing a contract in a modern office"
    image_url = generate_image(image_prompt)
    if image_url:
        print(f"プロンプト「{image_prompt}」で生成された画像URL:")
        print(image_url)
    
    print("\n=== ストリーミングレスポンスサンプル ===")
    streaming_question = "契約書における不可抗力条項の重要性について説明してください。"
    chat_with_streaming(legal_system_prompt, streaming_question) 