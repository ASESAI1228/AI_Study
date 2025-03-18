# Docker環境の構築と活用

## Dockerとは

- コンテナ型の仮想化技術
- アプリケーションとその依存関係をパッケージ化
- 「ビルドは一度、どこでも実行」の原則
- 開発環境と本番環境の一貫性を確保
- マイクロサービスアーキテクチャの実現に最適

## Dockerのメリット

- 環境の一貫性（"It works on my machine"問題の解消）
- 迅速なデプロイメント
- リソース効率の向上
- スケーラビリティの向上
- 分離とセキュリティ
- CI/CDパイプラインとの統合

## Dockerの基本概念

- **イメージ**：アプリケーションとその実行環境を含む不変のテンプレート
- **コンテナ**：イメージのインスタンス、実行中のアプリケーション
- **Dockerfile**：イメージをビルドするための指示書
- **レジストリ**：イメージを保存・共有するリポジトリ（Docker Hub等）
- **ボリューム**：データの永続化のための仕組み
- **ネットワーク**：コンテナ間通信のための仕組み

## Dockerのインストールと基本コマンド

### インストール
- Windows: Docker Desktop for Windows
- macOS: Docker Desktop for Mac
- Linux: パッケージマネージャを使用

### 基本コマンド

```bash
# バージョン確認
docker --version

# イメージの一覧表示
docker images

# コンテナの一覧表示
docker ps -a

# コンテナの実行
docker run -it --name my-python python:3.9 bash

# コンテナの停止
docker stop my-python

# コンテナの削除
docker rm my-python

# イメージの削除
docker rmi python:3.9
```

## Dockerfileの作成

### 基本構造

```dockerfile
# ベースイメージの指定
FROM python:3.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# 環境変数の設定
ENV PYTHONUNBUFFERED=1

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ポートの公開
EXPOSE 8000

# 実行コマンドの設定
CMD ["python", "app.py"]
```

### ビルドと実行

```bash
# イメージのビルド
docker build -t my-app:1.0 .

# コンテナの実行
docker run -p 8000:8000 my-app:1.0
```

## Docker Composeによる複数サービスの連携

### docker-compose.ymlの基本構造

```yaml
version: '3'

services:
  web:
    build: ./web
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/mydb
    depends_on:
      - db
    volumes:
      - ./web:/app
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=mydb
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 基本コマンド

```bash
# サービスの起動
docker-compose up

# バックグラウンドでの起動
docker-compose up -d

# サービスの停止
docker-compose down

# サービスの再構築
docker-compose up --build
```

## 法務AIアプリケーションのコンテナ化

### アプリケーション構成

- Streamlitフロントエンド
- FastAPIバックエンド
- PostgreSQLデータベース
- Redis（キャッシュ）

### Streamlitアプリケーションのコンテナ化

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

### FastAPIバックエンドのコンテナ化

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 開発環境と本番環境の分離

### 環境別の設定

- 開発環境：ホットリロード、デバッグモード、ボリュームマウント
- 本番環境：最適化、セキュリティ強化、スケーリング

### 環境変数の管理

```yaml
# docker-compose.override.yml（開発環境）
version: '3'

services:
  web:
    environment:
      - DEBUG=True
      - LOG_LEVEL=DEBUG
    volumes:
      - ./web:/app
    command: ["streamlit", "run", "app.py", "--server.runOnSave=true"]

# docker-compose.prod.yml（本番環境）
version: '3'

services:
  web:
    environment:
      - DEBUG=False
      - LOG_LEVEL=INFO
    restart: always
    command: ["streamlit", "run", "app.py"]
```

## 次回予告：アプリケーションのデプロイと運用

- クラウド環境へのデプロイ
- CI/CDパイプラインの構築
- モニタリングとロギング
- スケーリングとパフォーマンス最適化
- セキュリティ対策 