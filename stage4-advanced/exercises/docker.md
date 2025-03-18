# Docker環境構築演習

## 目的

この演習では、Dockerを使用して法務アプリケーションの開発・実行環境を構築する方法を学びます。コンテナ技術の基本概念を理解し、Dockerfileの作成、Docker Composeによる複数コンテナの管理、本番環境へのデプロイ準備までの一連の流れを習得することを目的としています。

## 準備

1. Dockerをインストールしてください
   - Windows: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
   - macOS: [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
   - Linux: ディストリビューションに応じたパッケージマネージャでインストール

2. 動作確認を行ってください
   ```bash
   docker --version
   docker-compose --version
   ```

3. 前回の演習で作成したStreamlitアプリケーションを用意してください
   - 用意できない場合は、`code-examples/docker_app`のサンプルを使用してください

## 演習1：基本的なDockerコマンドの実習

### 課題1-1：Dockerイメージの操作

1. 以下のコマンドを実行して、Pythonの公式イメージを取得してください
   ```bash
   docker pull python:3.9-slim
   ```

2. 取得したイメージを確認してください
   ```bash
   docker images
   ```

3. 取得したイメージを使用して、一時的なコンテナを起動し、Pythonのバージョンを確認してください
   ```bash
   docker run --rm python:3.9-slim python --version
   ```

### 課題1-2：対話的なコンテナの操作

1. 対話モードでPythonコンテナを起動してください
   ```bash
   docker run -it --name python-test python:3.9-slim bash
   ```

2. コンテナ内で以下のコマンドを実行してください
   ```bash
   python -c "print('Hello from Docker container!')"
   pip install pandas
   python -c "import pandas as pd; print(pd.__version__)"
   exit
   ```

3. コンテナの状態を確認し、停止したコンテナを削除してください
   ```bash
   docker ps -a
   docker rm python-test
   ```

## 演習2：Dockerfileの作成と活用

### 課題2-1：基本的なDockerfileの作成

1. 新しいディレクトリを作成し、その中に移動してください
   ```bash
   mkdir legal-app
   cd legal-app
   ```

2. 以下の内容で簡単なPythonアプリケーション（app.py）を作成してください
   ```python
   # app.py
   import os
   import time
   
   print("法務文書管理システム - Docker版")
   print("=" * 40)
   print(f"環境変数 APP_ENV: {os.getenv('APP_ENV', '未設定')}")
   print("サーバーが起動しました。Ctrl+Cで終了します。")
   
   try:
       while True:
           time.sleep(1)
   except KeyboardInterrupt:
       print("サーバーを終了します。")
   ```

3. 以下の内容でDockerfileを作成してください
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY app.py .
   
   ENV APP_ENV=development
   
   CMD ["python", "app.py"]
   ```

4. Dockerイメージをビルドしてください
   ```bash
   docker build -t legal-app:1.0 .
   ```

5. ビルドしたイメージからコンテナを実行してください
   ```bash
   docker run --name legal-app-container legal-app:1.0
   ```

6. 別のターミナルから、実行中のコンテナを停止して削除してください
   ```bash
   docker stop legal-app-container
   docker rm legal-app-container
   ```

### 課題2-2：環境変数とボリュームの活用

1. 環境変数を指定してコンテナを実行してください
   ```bash
   docker run --name legal-app-container -e APP_ENV=production legal-app:1.0
   ```

2. アプリケーションを修正し、ボリュームマウントを使用して変更を反映させてください
   - app.pyを修正して、現在時刻を表示する機能を追加
   ```python
   # app.py に以下を追加
   from datetime import datetime
   
   # 既存のコードの適切な場所に挿入
   print(f"現在時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
   ```

3. ボリュームマウントを使用してコンテナを実行してください
   ```bash
   docker run --name legal-app-container -v $(pwd):/app legal-app:1.0
   ```

## 演習3：Streamlitアプリケーションのコンテナ化

### 課題3-1：Streamlitアプリケーションのコンテナ化

1. 前回の演習で作成したStreamlitアプリケーション（または`code-examples/docker_app`のサンプル）を使用して、以下の内容のDockerfileを作成してください
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app.py"]
   ```

2. requirements.txtファイルを作成してください
   ```
   streamlit==1.22.0
   pandas==1.5.3
   matplotlib==3.7.1
   psycopg2-binary==2.9.6
   python-dotenv==1.0.0
   openai==0.27.8
   ```

3. Dockerイメージをビルドしてください
   ```bash
   docker build -t legal-streamlit-app:1.0 .
   ```

4. ビルドしたイメージからコンテナを実行してください
   ```bash
   docker run -p 8501:8501 legal-streamlit-app:1.0
   ```

5. ブラウザで http://localhost:8501 にアクセスして、アプリケーションが正常に動作することを確認してください

### 課題3-2：開発環境の最適化

1. 以下の内容で.dockerignoreファイルを作成してください
   ```
   __pycache__/
   *.py[cod]
   *$py.class
   .env
   .venv
   venv/
   ENV/
   .git/
   .gitignore
   ```

2. ホットリロードを有効にして開発効率を向上させるために、以下のコマンドでコンテナを実行してください
   ```bash
   docker run -p 8501:8501 -v $(pwd):/app legal-streamlit-app:1.0
   ```

3. アプリケーションに小さな変更を加えて、変更が自動的に反映されることを確認してください

## 演習4：Docker Composeによる複数コンテナの管理

### 課題4-1：Docker Compose設定ファイルの作成

1. 以下の内容でdocker-compose.ymlファイルを作成してください
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

2. Docker Composeを使用してサービスを起動してください
   ```bash
   docker-compose up
   ```

3. 別のターミナルから、実行中のコンテナを確認してください
   ```bash
   docker-compose ps
   ```

4. サービスを停止してください
   ```bash
   docker-compose down
   ```

### 課題4-2：データベース初期化スクリプトの追加

1. dbディレクトリを作成し、その中にinit.sqlファイルを作成してください
   ```bash
   mkdir -p db/init
   ```

2. 以下の内容でdb/init/init.sqlファイルを作成してください
   ```sql
   -- 契約書タイプテーブル
   CREATE TABLE IF NOT EXISTS contract_types (
       id SERIAL PRIMARY KEY,
       name VARCHAR(100) NOT NULL,
       description TEXT
   );
   
   -- 取引先テーブル
   CREATE TABLE IF NOT EXISTS counterparties (
       id SERIAL PRIMARY KEY,
       name VARCHAR(200) NOT NULL,
       address TEXT,
       contact_person VARCHAR(100),
       email VARCHAR(100),
       phone VARCHAR(20)
   );
   
   -- 契約書テーブル
   CREATE TABLE IF NOT EXISTS contracts (
       id SERIAL PRIMARY KEY,
       title VARCHAR(200) NOT NULL,
       contract_type_id INTEGER REFERENCES contract_types(id),
       counterparty_id INTEGER REFERENCES counterparties(id),
       status VARCHAR(50) DEFAULT '下書き',
       effective_date DATE,
       expiration_date DATE,
       content TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   
   -- サンプルデータ
   INSERT INTO contract_types (name, description) VALUES
       ('秘密保持契約', '機密情報の取り扱いに関する契約'),
       ('業務委託契約', '業務の委託に関する契約'),
       ('ライセンス契約', '知的財産の使用許諾に関する契約'),
       ('売買契約', '物品の売買に関する契約');
   
   INSERT INTO counterparties (name, address, contact_person, email, phone) VALUES
       ('株式会社テックイノベーション', '東京都千代田区丸の内1-1-1', '山田太郎', 'yamada@tech-innovation.co.jp', '03-1234-5678'),
       ('株式会社法務パートナーズ', '東京都港区六本木6-6-6', '鈴木一郎', 'suzuki@legal-partners.co.jp', '03-8765-4321'),
       ('グローバルコンサルティング株式会社', '大阪府大阪市北区梅田2-2-2', '佐藤花子', 'sato@global-consulting.co.jp', '06-2345-6789');
   ```

3. docker-compose.ymlファイルを修正して、初期化スクリプトを使用するようにしてください
   ```yaml
   db:
     image: postgres:13
     volumes:
       - postgres_data:/var/lib/postgresql/data
       - ./db/init:/docker-entrypoint-initdb.d
     environment:
       - POSTGRES_PASSWORD=password
       - POSTGRES_DB=legaldb
     ports:
       - "5432:5432"
   ```

4. 修正したDocker Compose設定でサービスを起動してください
   ```bash
   docker-compose up
   ```

5. アプリケーションがデータベースに正常に接続され、サンプルデータが表示されることを確認してください

## 演習5：本番環境へのデプロイ準備

### 課題5-1：マルチステージビルドの実装

1. 以下の内容でマルチステージビルドを使用するDockerfileを作成してください
   ```dockerfile
   # ビルドステージ
   FROM python:3.9-slim AS builder
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # 実行ステージ
   FROM python:3.9-slim
   
   WORKDIR /app
   
   # ビルドステージからパッケージをコピー
   COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
   COPY --from=builder /usr/local/bin /usr/local/bin
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app.py"]
   ```

2. マルチステージビルドを使用してイメージをビルドしてください
   ```bash
   docker build -t legal-app:production .
   ```

3. 本番環境用の設定を含む.env.productionファイルを作成してください
   ```
   DB_HOST=db
   DB_NAME=legaldb
   DB_USER=postgres
   DB_PASS=secure_password
   OPENAI_API_KEY=your_api_key
   ```

4. 本番環境用のdocker-compose.production.ymlファイルを作成してください
   ```yaml
   version: '3'
   
   services:
     web:
       image: legal-app:production
       restart: always
       ports:
         - "8501:8501"
       env_file:
         - .env.production
       depends_on:
         - db
     
     db:
       image: postgres:13
       restart: always
       volumes:
         - postgres_data:/var/lib/postgresql/data
         - ./db/init:/docker-entrypoint-initdb.d
       env_file:
         - .env.production
       environment:
         - POSTGRES_PASSWORD=${DB_PASS}
         - POSTGRES_DB=${DB_NAME}
   
   volumes:
     postgres_data:
   ```

### 課題5-2：コンテナレジストリの活用

1. Docker Hubアカウントを作成してください（既にある場合はスキップ）

2. ローカルでDocker Hubにログインしてください
   ```bash
   docker login
   ```

3. 本番用イメージにタグを付けてください（usernameは自分のDocker Hubユーザー名に置き換えてください）
   ```bash
   docker tag legal-app:production username/legal-app:latest
   ```

4. イメージをDocker Hubにプッシュしてください
   ```bash
   docker push username/legal-app:latest
   ```

5. プッシュしたイメージを使用するように、docker-compose.production.ymlファイルを修正してください
   ```yaml
   web:
     image: username/legal-app:latest
     # 他の設定は変更なし
   ```

## 提出課題

以上の演習を通じて学んだことを活かして、以下の課題に取り組んでください：

1. 法務文書管理システムのDockerコンテナ環境を構築してください
   - Streamlitアプリケーション
   - PostgreSQLデータベース
   - 必要に応じて追加のサービス（Redis, Elasticsearch等）

2. 以下の要件を満たすようにしてください：
   - 開発環境と本番環境の設定分離
   - セキュリティ対策の実装
   - パフォーマンス最適化
   - CI/CDパイプラインとの連携を考慮した設計

3. 以下の内容を含むレポートを作成してください（800〜1,200字程度）：
   - コンテナ化の方針と設計思想
   - 開発環境と本番環境の違いと対応方法
   - セキュリティ対策の詳細
   - デプロイ手順と運用方法
   - 今後の改善点

4. 構築した環境のデモンストレーション動画（3分程度）を作成してください

提出方法：研修用ポータルサイトの課題提出ページからDockerfile、docker-compose.yml、ソースコード、レポート、デモ動画をアップロードしてください。 