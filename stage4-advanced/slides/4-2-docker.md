# Docker環境の構築と活用

## Dockerとは

- コンテナ型の仮想化技術
- アプリケーションとその依存関係をパッケージ化
- 「どこでも同じように動く」環境を提供
- 開発・テスト・本番環境の一貫性を確保

## コンテナとは

- 軽量な仮想化技術
- ホストOSのカーネルを共有
- 仮想マシン（VM）より起動が速く、リソース効率が高い
- 必要なライブラリやアプリケーションのみを含む

## Dockerの主要コンポーネント

- Docker Engine: コンテナの実行環境
- Docker Image: コンテナの設計図（テンプレート）
- Docker Container: 実行中のインスタンス
- Docker Registry: イメージの保存・共有場所（Docker Hub等）
- Dockerfile: イメージをビルドするための指示書
- Docker Compose: 複数コンテナの定義・実行ツール

## Dockerのインストール

### Windows
- Docker Desktop for Windows
- WSL2（Windows Subsystem for Linux）の有効化推奨

### macOS
- Docker Desktop for Mac
- Apple Silicon対応版も利用可能

### Linux
- ディストリビューションに応じたパッケージマネージャで導入
```bash
# Ubuntu
sudo apt update
sudo apt install docker.io docker-compose
```

## 基本的なDockerコマンド

```bash
# イメージの取得
docker pull python:3.9

# コンテナの作成と起動
docker run -it --name my-python python:3.9 bash

# コンテナの一覧表示
docker ps -a

# コンテナの起動/停止
docker start my-python
docker stop my-python

# コンテナの削除
docker rm my-python

# イメージの一覧表示
docker images

# イメージの削除
docker rmi python:3.9
```

## Dockerfileの作成

```dockerfile
# ベースイメージの指定
FROM python:3.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なファイルのコピー
COPY requirements.txt .

# 依存パッケージのインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコピー
COPY . .

# 環境変数の設定
ENV PYTHONUNBUFFERED=1

# ポートの公開
EXPOSE 8000

# コンテナ起動時に実行するコマンド
CMD ["python", "app.py"]
```

## Dockerfileのビルドと実行

```bash
# イメージのビルド
docker build -t legal-app:1.0 .

# コンテナの実行
docker run -p 8000:8000 legal-app:1.0

# バインドマウントを使用した実行（開発時）
docker run -p 8000:8000 -v $(pwd):/app legal-app:1.0
```

## Docker Composeの活用

### docker-compose.ymlの例

```yaml
version: '3'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/legaldb
  
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=legaldb

volumes:
  postgres_data:
```

### Docker Composeコマンド

```bash
# サービスの起動
docker-compose up

# バックグラウンドで起動
docker-compose up -d

# サービスの停止
docker-compose down

# サービスの再構築
docker-compose up --build
```

## 法務アプリケーションのコンテナ化

### 法務文書管理システムの例

【python】
# app.py
import os
import streamlit as st
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# データベース接続情報
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "legaldb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")

# Streamlitアプリケーション
def main():
    st.title("法務文書管理システム")
    
    # サイドバーメニュー
    menu = st.sidebar.selectbox(
        "メニュー",
        ["契約書一覧", "契約書登録", "契約書検索", "分析ダッシュボード"]
    )
    
    if menu == "契約書一覧":
        st.header("契約書一覧")
        # データベースから契約書一覧を取得して表示
        conn = get_db_connection()
        if conn:
            df = pd.read_sql("SELECT * FROM contracts", conn)
            st.dataframe(df)
            conn.close()

# データベース接続
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        st.error(f"データベース接続エラー: {e}")
        return None

if __name__ == "__main__":
    main()
【python】

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

### docker-compose.yml

```yaml
version: '3'

services:
  web:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - .:/app
    depends_on:
      - db
    environment:
      - DB_HOST=db
      - DB_NAME=legaldb
      - DB_USER=postgres
      - DB_PASS=password
  
  db:
    image: postgres:13
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=legaldb
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## 本番環境へのデプロイ

### コンテナレジストリの活用

- Docker Hub
- GitHub Container Registry
- AWS ECR, Google GCR, Azure ACR

```bash
# イメージのタグ付け
docker tag legal-app:1.0 username/legal-app:1.0

# イメージのプッシュ
docker login
docker push username/legal-app:1.0
```

### クラウドサービスでの実行

- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances
- Heroku Container Registry

## セキュリティのベストプラクティス

- 最小権限の原則
- 公式イメージの使用
- マルチステージビルド
- シークレット管理
- イメージスキャン
- 不要なパッケージの削除

## 次回予告：RAG（検索拡張生成）の実装

- ベクトルデータベースの基礎
- 埋め込みモデルの活用
- 検索拡張生成の仕組み
- 法務文書のRAGシステム構築 