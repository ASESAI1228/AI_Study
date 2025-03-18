# Anthropic Claude API 利用サンプル

# 必要なライブラリのインストール
# pip install anthropic
# pip install python-dotenv

import anthropic
import os
from dotenv import load_dotenv
import time

# .envファイルから環境変数を読み込む
load_dotenv()

# APIキーの設定
api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)

# 利用可能なモデルを表示する関数
def list_models():
    try:
        # Anthropic APIでは直接モデル一覧を取得するエンドポイントがないため、
        # 主要なモデルを手動でリスト化
        models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2"
        ]
        print("利用可能なClaudeモデル:")
        for model in models:
            print(f"- {model}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# テキスト生成を行う関数
def generate_text(prompt, model="claude-3-sonnet-20240229", max_tokens=1000):
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# チャット形式で対話する関数
def chat_with_claude(system_prompt, user_prompt, model="claude-3-sonnet-20240229", max_tokens=1000):
    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.content[0].text
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

# ストリーミングレスポンスを使用する関数
def generate_text_streaming(prompt, model="claude-3-sonnet-20240229", max_tokens=1000):
    try:
        with client.messages.stream(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        ) as stream:
            print("Claudeの回答（ストリーミング）:")
            for text in stream.text_stream:
                print(text, end="", flush=True)
            print("\n")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 長文処理の例（Claudeは長いコンテキスト処理が得意）
def analyze_long_document(document, question, model="claude-3-opus-20240229"):
    try:
        prompt = f"""
以下の文書を分析して、質問に答えてください。

文書:
{document}

質問:
{question}
"""
        response = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
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

# サンプル契約書
sample_contract = """
秘密保持契約書

株式会社〇〇〇〇（以下「甲」という）と株式会社△△△△（以下「乙」という）は、両者間の秘密情報の取扱いに関し、以下のとおり契約（以下「本契約」という）を締結する。

第1条（目的）
本契約は、甲乙間の業務提携の検討（以下「本件協議」という）にあたり、相互に開示する秘密情報の取扱いを定めることを目的とする。

第2条（秘密保持義務）
1. 甲および乙は、相手方から開示された秘密情報を厳に秘密として保持し、事前に相手方の書面による承諾を得ることなく、第三者に開示、漏洩してはならない。
2. 前項の規定にかかわらず、次の各号のいずれかに該当する情報については、秘密情報から除外するものとする。
   (1) 開示を受けた時点で既に公知となっていた情報
   (2) 開示を受けた後、自己の責によらず公知となった情報
   (3) 開示を受けた時点で既に自己が保有していた情報
   (4) 正当な権限を有する第三者から秘密保持義務を負うことなく適法に取得した情報
   (5) 秘密情報を利用することなく独自に開発した情報

第3条（目的外使用の禁止）
甲および乙は、秘密情報を本件協議の目的以外の目的で使用してはならない。

第4条（複製等の禁止）
甲および乙は、相手方の事前の書面による承諾なく、秘密情報を記録した書面その他の記録媒体を複製または複写してはならない。

第5条（秘密情報の返還）
甲および乙は、相手方から請求があった場合または本件協議が終了した場合、直ちに相手方から開示された秘密情報およびその複製物を相手方に返還または破棄し、その旨を証する書面を相手方に提出するものとする。

第6条（損害賠償）
甲または乙が本契約に違反して相手方に損害を与えた場合、違反当事者は相手方に対し、その損害を賠償する責任を負うものとする。

第7条（有効期間）
1. 本契約の有効期間は、本契約締結の日から2年間とする。
2. 前項の規定にかかわらず、第2条（秘密保持義務）、第3条（目的外使用の禁止）および第6条（損害賠償）の規定は、本契約終了後も3年間効力を有するものとする。

第8条（協議事項）
本契約に定めのない事項または本契約の解釈に疑義が生じた場合、甲乙誠意をもって協議のうえ解決するものとする。

第9条（準拠法および管轄裁判所）
本契約の準拠法は日本法とし、本契約に関する一切の紛争については、東京地方裁判所を第一審の専属的合意管轄裁判所とする。

以上、本契約の成立を証するため、本書2通を作成し、甲乙記名押印のうえ、各1通を保有する。

20XX年XX月XX日

甲：東京都千代田区〇〇町1-1-1
   株式会社〇〇〇〇
   代表取締役 〇〇 〇〇

乙：東京都港区△△町2-2-2
   株式会社△△△△
   代表取締役 △△ △△
"""

# メイン処理
if __name__ == "__main__":
    print("Anthropic Claude APIサンプルプログラム\n")
    
    # 利用可能なモデルを表示
    list_models()
    
    print("\n=== テキスト生成サンプル ===")
    text_prompt = "法律文書における「甲」「乙」の使い方と由来について説明してください。"
    response = generate_text(text_prompt)
    print(f"プロンプト: {text_prompt}")
    print(f"回答: {response}\n")
    
    print("=== チャットサンプル ===")
    user_question = "秘密保持契約（NDA）の主要な条項と注意点について教えてください。"
    chat_response = chat_with_claude(legal_system_prompt, user_question)
    print(f"質問: {user_question}")
    print(f"回答: {chat_response}\n")
    
    print("=== ストリーミングレスポンスサンプル ===")
    streaming_prompt = "契約書における準拠法と管轄裁判所の条項の重要性について説明してください。"
    generate_text_streaming(streaming_prompt)
    
    print("=== 長文分析サンプル ===")
    question = "この契約書の秘密保持義務の期間はどのように定められていますか？また、秘密情報から除外される情報は何ですか？"
    long_doc_response = analyze_long_document(sample_contract, question)
    print(f"質問: {question}")
    print(f"回答: {long_doc_response}") 