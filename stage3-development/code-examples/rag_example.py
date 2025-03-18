# RAG（検索拡張生成）の基本実装例

import os
import numpy as np
from dotenv import load_dotenv
import openai
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import re
import json

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# サンプルの法律文書データ
legal_documents = [
    {
        "id": 1,
        "title": "秘密保持契約書",
        "content": """
        第1条（目的）
        本契約は、甲乙間の業務提携の検討にあたり、相互に開示する秘密情報の取扱いを定めることを目的とする。

        第2条（秘密情報の定義）
        本契約において「秘密情報」とは、甲または乙が相手方に開示する技術上、営業上の一切の情報であって、以下の各号のいずれかに該当するものをいう。
        (1) 書面、電子メール等有形の媒体により開示される情報であって、「秘密」「Confidential」等の表示がなされたもの
        (2) 口頭、デモンストレーション等により開示される情報であって、開示の際に秘密である旨が明示され、かつ開示後14日以内に書面により内容が特定されたもの
        """
    },
    {
        "id": 2,
        "title": "業務委託契約書",
        "content": """
        第1条（目的）
        甲は、以下に定める業務を乙に委託し、乙はこれを受託する。

        第2条（委託業務）
        乙が甲から委託を受ける業務（以下「本業務」という）の内容は、以下のとおりとする。
        (1) 法務文書の作成支援
        (2) 契約書レビュー
        (3) 法律相談対応
        """
    },
    {
        "id": 3,
        "title": "雇用契約書",
        "content": """
        第1条（雇用）
        会社は従業員を雇用し、従業員はこれを承諾する。

        第2条（職務内容）
        従業員は、会社の指示に従い、法務部において法務業務に従事するものとする。会社は、業務上の必要性に応じて、従業員の職務内容を変更することができる。
        """
    },
    {
        "id": 4,
        "title": "賃貸借契約書",
        "content": """
        第1条（物件）
        賃貸人は、次の物件を賃借人に賃貸し、賃借人はこれを賃借する。
        所在地：東京都千代田区〇〇町1-1-1
        建物名：〇〇ビル 3階301号室
        種類：事務所
        面積：80平方メートル

        第2条（賃料）
        賃料は月額30万円とし、賃借人は毎月末日までに翌月分を賃貸人の指定する銀行口座に振り込むものとする。
        """
    }
]

# 文書をベクトル化するための関数
def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    response = openai.Embedding.create(
        input=[text],
        model=model
    )
    return response["data"][0]["embedding"]

# 文書のインデックスを作成する関数
def create_document_index(documents):
    document_embeddings = []
    
    print("文書のインデックスを作成中...")
    for doc in documents:
        # タイトルと内容を結合してベクトル化
        content = f"{doc['title']}: {doc['content']}"
        embedding = get_embedding(content)
        document_embeddings.append({
            "id": doc["id"],
            "title": doc["title"],
            "embedding": embedding
        })
    
    print(f"{len(document_embeddings)}件の文書をインデックス化しました")
    return document_embeddings

# 類似文書を検索する関数
def search_similar_documents(query, document_embeddings, top_n=2):
    # クエリをベクトル化
    query_embedding = get_embedding(query)
    
    # 類似度を計算
    similarities = []
    for doc in document_embeddings:
        similarity = cosine_similarity(
            [query_embedding],
            [doc["embedding"]]
        )[0][0]
        similarities.append({
            "id": doc["id"],
            "title": doc["title"],
            "similarity": similarity
        })
    
    # 類似度でソート
    sorted_similarities = sorted(similarities, key=lambda x: x["similarity"], reverse=True)
    
    # 上位N件を返す
    return sorted_similarities[:top_n]

# 検索結果から関連文書の内容を取得する関数
def get_document_contents(doc_ids, documents):
    contents = []
    for doc_id in doc_ids:
        for doc in documents:
            if doc["id"] == doc_id:
                contents.append(f"タイトル: {doc['title']}\n\n{doc['content']}")
                break
    return contents

# RAGを使用して質問に回答する関数
def answer_with_rag(query, documents, document_embeddings):
    # 類似文書を検索
    similar_docs = search_similar_documents(query, document_embeddings)
    
    # 検索結果のIDを取得
    doc_ids = [doc["id"] for doc in similar_docs]
    
    # 関連文書の内容を取得
    relevant_contents = get_document_contents(doc_ids, documents)
    
    # 関連文書を結合
    context = "\n\n---\n\n".join(relevant_contents)
    
    # プロンプトを作成
    prompt = f"""以下の文書に基づいて質問に回答してください。
文書に明示されていない情報については、「提供された文書からはわかりません」と回答してください。

===文書===
{context}

===質問===
{query}
"""
    
    # OpenAI APIを使用して回答を生成
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは法務アシスタントです。提供された文書に基づいて質問に回答してください。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return {
        "answer": response.choices[0].message["content"],
        "sources": [{"id": doc["id"], "title": doc["title"], "similarity": f"{doc['similarity']:.4f}"} for doc in similar_docs]
    }

# メイン処理
if __name__ == "__main__":
    print("RAG（検索拡張生成）サンプルプログラム\n")
    
    # 文書のインデックスを作成
    document_embeddings = create_document_index(legal_documents)
    
    # ユーザーからの質問例
    questions = [
        "秘密情報の定義について教えてください",
        "業務委託契約における委託業務の内容は何ですか",
        "賃料はいくらで、いつ支払う必要がありますか",
        "契約書における不可抗力条項について教えてください"  # 文書にない情報
    ]
    
    # 各質問に回答
    for i, question in enumerate(questions):
        print(f"\n質問 {i+1}: {question}")
        
        result = answer_with_rag(question, legal_documents, document_embeddings)
        
        print("\n回答:")
        print(result["answer"])
        
        print("\n参照文書:")
        for source in result["sources"]:
            print(f"- {source['title']} (類似度: {source['similarity']})")
        
        print("-" * 80) 