# RAG（検索拡張生成）の実装

## RAGとは

- Retrieval-Augmented Generation（検索拡張生成）
- 大規模言語モデル（LLM）と情報検索を組み合わせた手法
- 外部知識ベースから関連情報を検索し、LLMの回答を強化
- 最新情報や専門知識を反映した回答が可能

## RAGのメリット

- 最新情報へのアクセス（LLMの学習データ以降の情報）
- 専門知識の正確な反映
- 幻覚（ハルシネーション）の低減
- ソース引用による透明性の向上
- データプライバシーの向上（機密情報をLLMに直接送信しない）

## RAGの基本アーキテクチャ

1. **インデックス作成**：文書をチャンクに分割し、ベクトル化して保存
2. **検索**：ユーザークエリをベクトル化し、類似度の高いチャンクを検索
3. **生成**：検索結果をコンテキストとしてLLMに提供し、回答を生成

## 文書の前処理とチャンキング

【python】
import re
import nltk
from nltk.tokenize import sent_tokenize

# 文書の前処理
def preprocess_document(text):
    # 余分な空白の削除
    text = re.sub(r'\s+', ' ', text).strip()
    # 特殊文字の処理
    text = re.sub(r'[^\w\s\.\,\;\:\-\(\)\[\]\{\}]', '', text)
    return text

# 文書のチャンキング（段落ベース）
def chunk_by_paragraph(text, max_chunk_size=1000):
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) <= max_chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# 文書のチャンキング（文ベース、オーバーラップあり）
def chunk_by_sentence(text, chunk_size=5, overlap=2):
    sentences = sent_tokenize(text)
    chunks = []
    
    for i in range(0, len(sentences) - chunk_size + 1, chunk_size - overlap):
        chunk = ' '.join(sentences[i:i+chunk_size])
        chunks.append(chunk)
    
    return chunks
【python】

## 埋め込みベクトルの生成

【python】
import openai
import numpy as np
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# テキストの埋め込みベクトル生成
def get_embedding(text):
    response = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

# 複数チャンクの埋め込みベクトル生成（バッチ処理）
def get_embeddings_batch(chunks, batch_size=100):
    all_embeddings = []
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        response = openai.embeddings.create(
            model="text-embedding-ada-002",
            input=batch
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
    
    return all_embeddings
【python】

## ベクトルデータベースの構築

【python】
import faiss
import pickle
import numpy as np

# FAISSインデックスの作成
def create_faiss_index(embeddings):
    # 埋め込みベクトルをNumPy配列に変換
    embeddings_np = np.array(embeddings, dtype=np.float32)
    
    # インデックスの作成（L2距離）
    dimension = embeddings_np.shape[1]  # ベクトルの次元数
    index = faiss.IndexFlatL2(dimension)
    
    # ベクトルの追加
    index.add(embeddings_np)
    
    return index

# インデックスと関連データの保存
def save_index(index, chunks, file_path="faiss_index.pkl"):
    with open(file_path, "wb") as f:
        pickle.dump({"index": faiss.serialize_index(index), "chunks": chunks}, f)

# インデックスと関連データの読み込み
def load_index(file_path="faiss_index.pkl"):
    with open(file_path, "rb") as f:
        data = pickle.load(f)
        index = faiss.deserialize_index(data["index"])
        chunks = data["chunks"]
    return index, chunks
【python】

## 検索機能の実装

【python】
# クエリの埋め込みベクトル生成
def get_query_embedding(query):
    return get_embedding(query)

# 類似度検索
def search_similar_chunks(index, query_embedding, chunks, k=5):
    # クエリベクトルをNumPy配列に変換
    query_np = np.array([query_embedding], dtype=np.float32)
    
    # 検索実行
    distances, indices = index.search(query_np, k)
    
    # 検索結果の整形
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(chunks) and idx >= 0:  # 有効なインデックスかチェック
            results.append({
                "chunk": chunks[idx],
                "distance": distances[0][i],
                "index": idx
            })
    
    return results
【python】

## 生成AIとの連携

【python】
# 検索結果を使用した回答生成
def generate_answer(query, search_results):
    # コンテキストの作成
    context = "\n\n".join([result["chunk"] for result in search_results])
    
    # プロンプトの構築
    prompt = f"""以下の情報に基づいて質問に回答してください。
情報源:
{context}

質問: {query}

回答:"""
    
    # OpenAI APIを使用して回答を生成
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは法務アシスタントです。与えられた情報源に基づいて正確に回答してください。情報源に含まれていない内容については、「提供された情報からは回答できません」と述べてください。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,  # 低い温度で決定論的な回答を生成
        max_tokens=500
    )
    
    return response.choices[0].message.content

# 情報源の引用を含む回答生成
def generate_answer_with_citations(query, search_results):
    # 各チャンクに引用IDを付与
    context_with_citations = ""
    for i, result in enumerate(search_results):
        citation_id = f"[{i+1}]"
        context_with_citations += f"{citation_id} {result['chunk']}\n\n"
    
    # プロンプトの構築
    prompt = f"""以下の情報に基づいて質問に回答してください。回答内で情報源を引用する場合は、対応する引用ID（例：[1]、[2]）を使用してください。

情報源:
{context_with_citations}

質問: {query}

回答（引用IDを含めてください）:"""
    
    # OpenAI APIを使用して回答を生成
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは法務アシスタントです。与えられた情報源に基づいて正確に回答し、適切な引用IDを使用してください。情報源に含まれていない内容については、「提供された情報からは回答できません」と述べてください。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    
    return response.choices[0].message.content
【python】

## RAGシステムの評価と最適化

### 評価指標
- 正確性（Accuracy）
- 関連性（Relevance）
- 完全性（Completeness）
- 応答時間（Response Time）

### 最適化ポイント
- チャンクサイズの調整
- 埋め込みモデルの選択
- 検索アルゴリズムの改良
- プロンプトエンジニアリング

## 実装例：法務文書RAGシステム

【python】
import streamlit as st
import openai
import faiss
import numpy as np
import os
import pickle
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# アプリケーションのタイトル
st.title("法務文書検索・質問応答システム")

# サイドバー：文書アップロード
st.sidebar.header("文書管理")
uploaded_file = st.sidebar.file_uploader("文書をアップロード", type=["txt", "pdf", "docx"])

if uploaded_file:
    # 文書の処理（実際の実装ではPDFやDOCXの処理も追加）
    document_text = uploaded_file.getvalue().decode("utf-8")
    
    if st.sidebar.button("文書をインデックス化"):
        with st.spinner("文書を処理中..."):
            # 文書の前処理とチャンキング
            chunks = chunk_by_paragraph(document_text)
            
            # 埋め込みベクトルの生成
            embeddings = get_embeddings_batch(chunks)
            
            # インデックスの作成
            index = create_faiss_index(embeddings)
            
            # セッションステートに保存
            st.session_state.index = index
            st.session_state.chunks = chunks
            
            st.sidebar.success(f"{len(chunks)}チャンクのインデックスを作成しました")

# メイン：質問応答
st.header("質問応答")
query = st.text_input("質問を入力してください")

if query and st.button("回答を生成"):
    if "index" in st.session_state and "chunks" in st.session_state:
        with st.spinner("回答を生成中..."):
            # クエリの埋め込みベクトル生成
            query_embedding = get_query_embedding(query)
            
            # 類似チャンクの検索
            search_results = search_similar_chunks(
                st.session_state.index, 
                query_embedding, 
                st.session_state.chunks, 
                k=3
            )
            
            # 回答の生成
            answer = generate_answer_with_citations(query, search_results)
            
            # 結果の表示
            st.subheader("回答")
            st.write(answer)
            
            # 参照情報の表示
            st.subheader("参照情報")
            for i, result in enumerate(search_results):
                with st.expander(f"参照 [{i+1}]"):
                    st.write(result["chunk"])
    else:
        st.error("文書をアップロードしてインデックス化してください")
【python】

## 次回予告：ファインチューニングの基礎

- ファインチューニングの概念と利点
- データセット準備の方法
- OpenAI APIを使用したファインチューニング
- ファインチューニング済みモデルの評価と活用 