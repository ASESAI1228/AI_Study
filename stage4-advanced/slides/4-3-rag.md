# RAG（検索拡張生成）の実装

## RAGとは

- Retrieval-Augmented Generation（検索拡張生成）
- 大規模言語モデル（LLM）の知識を外部データで拡張する手法
- 生成AIの幻覚（hallucination）問題を軽減
- 最新情報や専門知識を反映した回答が可能

## RAGの基本構造

1. **検索（Retrieval）**: ユーザークエリに関連する情報を外部データソースから検索
2. **拡張（Augmentation）**: 検索結果をプロンプトに追加
3. **生成（Generation）**: 拡張されたプロンプトを基にLLMが回答を生成

## RAGのメリット

- 最新情報や専門知識の反映
- 幻覚の軽減
- ドメイン特化型の回答生成
- プライベートデータの活用
- モデル再学習不要

## ベクトルデータベースの基礎

- テキストをベクトル（数値の配列）として表現
- 意味的類似性に基づく検索が可能
- 主要なベクトルデータベース
  - Pinecone
  - Weaviate
  - Milvus
  - Qdrant
  - Chroma
  - FAISS
  - PGVector (PostgreSQL拡張)

## 埋め込みモデル（Embedding Models）

- テキストを固定長のベクトルに変換するモデル
- 意味的に類似したテキストは、ベクトル空間で近い位置に配置される
- 主要な埋め込みモデル
  - OpenAI: text-embedding-ada-002
  - OpenAI: text-embedding-3-small/large
  - Cohere: embed-multilingual-v3.0
  - HuggingFace: sentence-transformers
  - BGE Embeddings

## 類似度検索

- コサイン類似度: ベクトル間の角度を測定
- ユークリッド距離: ベクトル間の直線距離を測定
- 内積: ベクトルの方向性の一致度を測定
- 近似最近傍探索（ANN）: 大規模データセットでの効率的な検索

## RAGシステムの構築手順

1. データの収集と前処理
2. テキストのチャンク分割
3. 埋め込みベクトルの生成
4. ベクトルデータベースへの保存
5. 検索機能の実装
6. LLMとの統合
7. 評価とチューニング

## データの前処理とチャンク分割

- ドキュメントの読み込み（PDF, Word, HTML等）
- テキスト抽出とクリーニング
- 適切なサイズへのチャンク分割
  - 固定サイズ（トークン数、文字数）
  - 意味的なまとまり（段落、セクション）
  - 重複（オーバーラップ）の設定

```python
def split_text_into_chunks(text, chunk_size=1000, overlap=200):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            # 文の途中で切らないように調整
            while end > start and text[end] not in ['.', '!', '?', '\n']:
                end -= 1
            if end == start:  # 適切な区切りが見つからない場合
                end = start + chunk_size
        
        chunks.append(text[start:end])
        start = end - overlap
    
    return chunks
```

## 埋め込みベクトルの生成

```python
import openai

def generate_embeddings(chunks):
    embeddings = []
    for chunk in chunks:
        response = openai.Embedding.create(
            input=chunk,
            model="text-embedding-3-small"
        )
        embedding = response['data'][0]['embedding']
        embeddings.append(embedding)
    
    return embeddings
```

## ベクトルデータベースの構築

### Chromaの例

```python
import chromadb

client = chromadb.Client()
collection = client.create_collection("legal_documents")

for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
    collection.add(
        ids=[f"doc_{i}"],
        embeddings=[embedding],
        metadatas=[{"source": "contract_template", "chunk": i}],
        documents=[chunk]
    )
```

### PGVectorの例

```python
import psycopg2
import numpy as np

conn = psycopg2.connect("dbname=legaldb user=postgres")
cur = conn.cursor()

# pgvectorの拡張機能を有効化
cur.execute("CREATE EXTENSION IF NOT EXISTS vector")

# ベクトルを格納するテーブルを作成
cur.execute("""
CREATE TABLE IF NOT EXISTS document_embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536),
    metadata JSONB
)
""")

# データの挿入
for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
    cur.execute(
        "INSERT INTO document_embeddings (content, embedding, metadata) VALUES (%s, %s, %s)",
        (chunk, np.array(embedding), json.dumps({"source": "contract_template", "chunk": i}))
    )

conn.commit()
```

## 検索機能の実装

### Chromaでの検索

```python
def search_documents(query, top_k=3):
    # クエリの埋め込みベクトルを生成
    query_embedding = openai.Embedding.create(
        input=query,
        model="text-embedding-3-small"
    )['data'][0]['embedding']
    
    # ベクトル検索を実行
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    return results['documents'][0]
```

### PGVectorでの検索

```python
def search_documents(query, top_k=3):
    # クエリの埋め込みベクトルを生成
    query_embedding = openai.Embedding.create(
        input=query,
        model="text-embedding-3-small"
    )['data'][0]['embedding']
    
    # ベクトル検索を実行
    cur.execute("""
    SELECT content, 1 - (embedding <=> %s) as similarity
    FROM document_embeddings
    ORDER BY similarity DESC
    LIMIT %s
    """, (np.array(query_embedding), top_k))
    
    results = cur.fetchall()
    return [r[0] for r in results]
```

## LLMとの統合

```python
def answer_question(query):
    # 関連ドキュメントを検索
    relevant_docs = search_documents(query, top_k=3)
    
    # コンテキストを含むプロンプトを作成
    context = "\n\n".join(relevant_docs)
    prompt = f"""以下のコンテキストを使用して、質問に答えてください。
    コンテキスト内に情報がない場合は、「情報がありません」と回答してください。
    
    コンテキスト:
    {context}
    
    質問: {query}
    
    回答:"""
    
    # LLMで回答を生成
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "あなたは法務の専門家です。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )
    
    return response.choices[0].message.content
```

## RAGの評価方法

- 正確性（Accuracy）: 回答の事実的正確さ
- 関連性（Relevance）: 回答と質問の関連度
- 網羅性（Comprehensiveness）: 回答の完全性
- 一貫性（Consistency）: 複数の質問に対する回答の一貫性
- 幻覚の割合（Hallucination Rate）: 事実と異なる情報の頻度

## RAGの最適化テクニック

- チャンクサイズの調整
- 埋め込みモデルの選択
- 検索結果数（top-k）の調整
- 再ランキング（Re-ranking）
- ハイパーパラメータチューニング
- プロンプトエンジニアリング

## 法務分野でのRAG活用例

- 契約書分析と質問応答
- 法令・判例検索
- コンプライアンスガイダンス
- デューデリジェンス支援
- 社内規定の検索と解釈

## 次回予告：クラウドデプロイメントとCI/CD

- クラウドプラットフォームの選択
- インフラストラクチャのコード化（IaC）
- CI/CDパイプラインの構築
- 自動テストと品質保証
- スケーラビリティとパフォーマンス最適化 