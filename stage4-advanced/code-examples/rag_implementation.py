# RAG（検索拡張生成）の実装例

import os
import json
import numpy as np
import pandas as pd
from typing import List, Dict, Any
import openai
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
import PyPDF2
import re
from tqdm import tqdm

# 環境変数の読み込み
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# 埋め込み関数の設定
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# ChromaDBクライアントの初期化
client = chromadb.Client()

# ===============================
# データ準備と前処理
# ===============================

def extract_text_from_pdf(pdf_path: str) -> str:
    """PDFからテキストを抽出する関数"""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

def clean_text(text: str) -> str:
    """テキストのクリーニングを行う関数"""
    # 余分な空白の削除
    text = re.sub(r'\s+', ' ', text)
    # 特殊文字の削除
    text = re.sub(r'[^\w\s\.\,\;\:\(\)\[\]\{\}\'\"\-\_\+\=\*\/\\\&\%\$\#\@\!\?\～\ー\「\」\（\）\［\］\｛\｝\・\：\；\，\。\！\？\＃\＄\％\＆\＊\＋\－\／\＝\＠\＼\＾\＿\｀\｜\～]', '', text)
    return text.strip()

def split_text_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """テキストを重複ありのチャンクに分割する関数"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        
        # 文の途中で切らないように調整
        if end < text_length:
            # 文末記号を探す
            sentence_end = max(
                text.rfind('. ', start, end),
                text.rfind('。', start, end),
                text.rfind('! ', start, end),
                text.rfind('？', start, end),
                text.rfind('\n', start, end)
            )
            
            if sentence_end > start:
                end = sentence_end + 1
            # 適切な区切りが見つからない場合はそのまま
        
        # チャンクを追加
        chunk = text[start:end].strip()
        if chunk:  # 空でない場合のみ追加
            chunks.append(chunk)
        
        # 次のチャンクの開始位置（重複あり）
        start = end - overlap
    
    return chunks

# ===============================
# 埋め込みベクトルの生成
# ===============================

def generate_embeddings(texts: List[str], model: str = "text-embedding-3-small") -> List[List[float]]:
    """テキストの埋め込みベクトルを生成する関数"""
    embeddings = []
    
    for text in tqdm(texts, desc="Generating embeddings"):
        response = openai.Embedding.create(
            input=text,
            model=model
        )
        embedding = response['data'][0]['embedding']
        embeddings.append(embedding)
    
    return embeddings

# ===============================
# ベクトルデータベースの構築
# ===============================

def create_vector_db(collection_name: str, chunks: List[str], metadata: List[Dict[str, Any]] = None) -> chromadb.Collection:
    """ChromaDBにベクトルデータベースを作成する関数"""
    # 既存のコレクションがあれば削除
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    # 新しいコレクションを作成
    collection = client.create_collection(
        name=collection_name,
        embedding_function=openai_ef
    )
    
    # メタデータがない場合は空のディクショナリのリストを作成
    if metadata is None:
        metadata = [{"source": "unknown", "chunk_id": i} for i in range(len(chunks))]
    
    # IDを生成
    ids = [f"doc_{i}" for i in range(len(chunks))]
    
    # データをバッチで追加（大量データの場合はバッチサイズを調整）
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        end = min(i + batch_size, len(chunks))
        collection.add(
            ids=ids[i:end],
            documents=chunks[i:end],
            metadatas=metadata[i:end]
        )
    
    return collection

# ===============================
# 検索機能
# ===============================

def search_documents(collection: chromadb.Collection, query: str, top_k: int = 3) -> Dict[str, Any]:
    """ベクトル検索を実行する関数"""
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    
    return results

# ===============================
# LLMとの統合
# ===============================

def generate_answer(query: str, context: List[str], model: str = "gpt-4") -> str:
    """検索結果を基にLLMで回答を生成する関数"""
    # コンテキストを結合
    context_text = "\n\n".join(context)
    
    # プロンプトの作成
    prompt = f"""以下のコンテキストを使用して、質問に答えてください。
コンテキスト内に情報がない場合は、「情報がありません」と回答してください。
回答は日本語で提供してください。

コンテキスト:
{context_text}

質問: {query}

回答:"""
    
    # LLMで回答を生成
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "あなたは法務の専門家です。正確で簡潔な回答を提供してください。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000
    )
    
    return response.choices[0].message.content

def answer_legal_question(collection: chromadb.Collection, query: str, top_k: int = 3) -> Dict[str, Any]:
    """法務質問に回答する関数"""
    # 関連ドキュメントを検索
    search_results = search_documents(collection, query, top_k)
    
    # 検索結果からコンテキストを抽出
    contexts = search_results['documents'][0]
    
    # LLMで回答を生成
    answer = generate_answer(query, contexts)
    
    # 結果を整形
    result = {
        "query": query,
        "answer": answer,
        "sources": search_results['metadatas'][0],
        "contexts": contexts
    }
    
    return result

# ===============================
# メイン処理
# ===============================

def process_legal_documents(pdf_dir: str, collection_name: str = "legal_documents") -> chromadb.Collection:
    """法務文書を処理してベクトルデータベースを構築する関数"""
    all_chunks = []
    all_metadata = []
    
    # PDFファイルを処理
    for filename in os.listdir(pdf_dir):
        if filename.endswith('.pdf'):
            file_path = os.path.join(pdf_dir, filename)
            print(f"Processing {filename}...")
            
            # テキスト抽出
            text = extract_text_from_pdf(file_path)
            
            # テキストクリーニング
            cleaned_text = clean_text(text)
            
            # チャンク分割
            chunks = split_text_into_chunks(cleaned_text)
            
            # メタデータ作成
            metadata = [{"source": filename, "chunk_id": i} for i in range(len(chunks))]
            
            all_chunks.extend(chunks)
            all_metadata.extend(metadata)
    
    # ベクトルデータベースの作成
    collection = create_vector_db(collection_name, all_chunks, all_metadata)
    
    print(f"Vector database created with {len(all_chunks)} chunks.")
    return collection

# ===============================
# 使用例
# ===============================

if __name__ == "__main__":
    # サンプル契約書テキスト
    sample_contracts = [
        """
        秘密保持契約書
        
        甲：株式会社法務テック（以下「甲」という）
        乙：株式会社AIソリューションズ（以下「乙」という）
        
        第1条（目的）
        本契約は、甲乙間の業務提携に関連して開示される秘密情報の取扱いを定めることを目的とする。
        
        第2条（秘密情報）
        本契約において秘密情報とは、甲または乙が相手方に開示する技術上、営業上の情報であって、秘密である旨を明示したものをいう。
        
        第3条（秘密保持義務）
        甲および乙は、相手方から開示された秘密情報を厳に秘密として保持し、第三者に開示または漏洩してはならない。
        
        第4条（損害賠償）
        本契約に違反して秘密情報を漏洩した場合、違反当事者は相手方に対して、一切の損害を賠償する責任を負う。
        
        第5条（契約期間）
        本契約は、2023年4月1日から2024年3月31日までとする。ただし、期間満了の1ヶ月前までに甲乙いずれからも書面による異議がない場合は、自動的に1年間延長されるものとする。
        
        第6条（準拠法および管轄裁判所）
        本契約の準拠法は日本法とし、本契約に関する紛争については東京地方裁判所を第一審の専属的合意管轄裁判所とする。
        
        以上、本契約の成立を証するため、本書2通を作成し、甲乙記名押印の上、各1通を保有する。
        
        2023年4月1日
        
        甲：東京都千代田区丸の内1-1-1
        　　株式会社法務テック
        　　代表取締役 法務 太郎
        
        乙：東京都港区六本木6-6-6
        　　株式会社AIソリューションズ
        　　代表取締役 AI 次郎
        """,
        
        """
        業務委託契約書
        
        委託者：株式会社法務テック（以下「委託者」という）
        受託者：株式会社AIソリューションズ（以下「受託者」という）
        
        第1条（委託業務）
        委託者は受託者に対し、以下の業務（以下「本業務」という）を委託し、受託者はこれを受託する。
        業務内容：法務文書管理システムの開発
        
        第2条（委託料）
        本業務の委託料は、月額50万円（税別）とする。委託者は受託者の請求に基づき、毎月末日までに受託者の指定する銀行口座に振り込むものとする。
        
        第3条（成果物の著作権）
        本業務の遂行により生じた成果物の著作権（著作権法第27条および第28条に定める権利を含む）は、委託者に帰属するものとする。
        
        第4条（秘密保持）
        受託者は、本業務の遂行にあたり知り得た委託者の秘密情報を、委託者の事前の書面による承諾なく第三者に開示または漏洩してはならない。
        
        第5条（契約期間）
        本契約の有効期間は、2023年5月1日から2024年4月30日までとする。
        
        第6条（解除）
        委託者または受託者は、相手方が本契約に違反し、相当の期間を定めて催告したにもかかわらず是正されないときは、本契約を解除することができる。
        
        第7条（準拠法および管轄裁判所）
        本契約の準拠法は日本法とし、本契約に関する紛争については東京地方裁判所を第一審の専属的合意管轄裁判所とする。
        
        以上、本契約の成立を証するため、本書2通を作成し、委託者および受託者記名押印の上、各1通を保有する。
        
        2023年5月1日
        
        委託者：東京都千代田区丸の内1-1-1
        　　　　株式会社法務テック
        　　　　代表取締役 法務 太郎
        
        受託者：東京都港区六本木6-6-6
        　　　　株式会社AIソリューションズ
        　　　　代表取締役 AI 次郎
        """
    ]
    
    # メタデータの作成
    metadata = [
        {"source": "秘密保持契約書", "type": "NDA", "party1": "株式会社法務テック", "party2": "株式会社AIソリューションズ", "date": "2023-04-01"},
        {"source": "業務委託契約書", "type": "業務委託", "party1": "株式会社法務テック", "party2": "株式会社AIソリューションズ", "date": "2023-05-01"}
    ]
    
    # サンプルデータからベクトルデータベースを作成
    print("Creating vector database...")
    collection = create_vector_db("sample_contracts", sample_contracts, metadata)
    
    # 質問例
    questions = [
        "秘密保持契約の期間はいつからいつまでですか？",
        "業務委託契約の委託料はいくらですか？",
        "成果物の著作権は誰に帰属しますか？",
        "契約の準拠法と管轄裁判所はどこですか？",
        "AIソリューションズ社の住所はどこですか？"
    ]
    
    # 質問に回答
    print("\n=== 法務質問応答デモ ===\n")
    for question in questions:
        print(f"質問: {question}")
        result = answer_legal_question(collection, question)
        print(f"回答: {result['answer']}")
        print(f"出典: {result['sources'][0]['source']}")
        print("-" * 50) 