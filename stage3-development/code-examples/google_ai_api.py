# Google AI (Gemini) API 利用サンプル

# 必要なライブラリのインストール
# pip install google-generativeai
# pip install python-dotenv

import google.generativeai as genai
import os
from dotenv import load_dotenv
import PIL.Image

# .envファイルから環境変数を読み込む
load_dotenv()

# APIキーの設定
genai.configure(api_key=os.getenv("GOOGLE_AI_API_KEY"))

# 利用可能なモデルを表示する関数
def list_models():
    try:
        models = genai.list_models()
        print("利用可能なモデル:")
        for model in models:
            print(f"- {model.name}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# テキスト生成を行う関数
def generate_text(prompt, model_name="gemini-pro"):
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# チャット形式で対話する関数
def chat_with_gemini(system_prompt, user_prompt, model_name="gemini-pro"):
    try:
        model = genai.GenerativeModel(model_name)
        
        # チャットセッションの開始
        chat = model.start_chat(history=[
            {"role": "user", "parts": [system_prompt]}
        ])
        
        # ユーザーからの質問を送信
        response = chat.send_message(user_prompt)
        return response.text
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# 画像とテキストを組み合わせたマルチモーダル処理
def process_image_and_text(image_path, prompt, model_name="gemini-pro-vision"):
    try:
        model = genai.GenerativeModel(model_name)
        
        # 画像の読み込み
        image = PIL.Image.open(image_path)
        
        # 画像とテキストを送信
        response = model.generate_content([image, prompt])
        return response.text
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# 埋め込みベクトルを取得する関数
def get_embedding(text, model_name="embedding-001"):
    try:
        embedding_model = genai.get_model(f"models/{model_name}")
        result = embedding_model.embed_content(
            model=f"models/{model_name}",
            content=text,
            task_type="retrieval_document"
        )
        return result["embedding"]
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# ストリーミングレスポンスを使用したテキスト生成
def generate_text_streaming(prompt, model_name="gemini-pro"):
    try:
        model = genai.GenerativeModel(model_name)
        
        # ストリーミングレスポンスを有効化
        response = model.generate_content(
            prompt,
            stream=True
        )
        
        print("Geminiの回答（ストリーミング）:")
        for chunk in response:
            print(chunk.text, end="", flush=True)
        print("\n")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 法務関連のプロンプト例
legal_system_prompt = """
あなたは経験豊富な法務アシスタントです。
契約書のレビューや法的アドバイスを提供します。
専門用語を適切に使いながらも、わかりやすく説明してください。
日本の法律に基づいた回答を心がけてください。
"""

# メイン処理
if __name__ == "__main__":
    print("Google AI (Gemini) APIサンプルプログラム\n")
    
    # 利用可能なモデルを表示
    list_models()
    
    print("\n=== テキスト生成サンプル ===")
    text_prompt = "著作権法の基本的な概念について、500字程度で説明してください。"
    response = generate_text(text_prompt)
    print(f"プロンプト: {text_prompt}")
    print(f"回答: {response}\n")
    
    print("=== チャットサンプル ===")
    user_question = "個人情報保護法における「個人情報」の定義と、企業が注意すべき点を教えてください。"
    chat_response = chat_with_gemini(legal_system_prompt, user_question)
    print(f"質問: {user_question}")
    print(f"回答: {chat_response}\n")
    
    print("=== 埋め込みベクトルサンプル ===")
    text_to_embed = "この契約は、甲と乙の間で締結される秘密保持契約である。"
    embedding = get_embedding(text_to_embed)
    if embedding:
        print(f"テキスト「{text_to_embed}」の埋め込みベクトル（最初の5要素）:")
        print(embedding[:5])
        print(f"ベクトルの次元数: {len(embedding)}\n")
    
    print("=== ストリーミングレスポンスサンプル ===")
    streaming_prompt = "企業間取引における契約書の重要性について説明してください。"
    generate_text_streaming(streaming_prompt)
    
    # 注: 画像処理サンプルは画像ファイルが必要なため、コメントアウト
    """
    print("=== 画像処理サンプル ===")
    image_path = "contract_image.jpg"  # 画像ファイルのパス
    image_prompt = "この契約書の主な条項を特定し、簡潔に説明してください。"
    if os.path.exists(image_path):
        image_response = process_image_and_text(image_path, image_prompt)
        print(f"プロンプト: {image_prompt}")
        print(f"回答: {image_response}")
    else:
        print(f"画像ファイル {image_path} が見つかりません。")
    """ 