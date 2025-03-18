# データベース連携

## データベースの基本概念

- データの永続的な保存と管理
- 構造化されたデータの効率的な検索と更新
- 複数ユーザーによる同時アクセスの制御
- データの整合性と安全性の確保

## Supabaseとは

- PostgreSQLベースのオープンソースBaaS（Backend as a Service）
- Firebase代替として人気の高いサービス
- リアルタイムデータベース、認証、ストレージなどの機能を提供
- RESTful APIとJavaScriptライブラリを提供

## データベース設計の基礎

### テーブル設計

【sql】
-- 契約書テーブルの作成
CREATE TABLE contracts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    contract_type VARCHAR(100) NOT NULL,
    effective_date DATE,
    expiration_date DATE,
    counterparty VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 契約書タグテーブルの作成
CREATE TABLE contract_tags (
    contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
    tag VARCHAR(50) NOT NULL,
    PRIMARY KEY (contract_id, tag)
);
【sql】

### リレーションシップ

- 一対一（One-to-One）
- 一対多（One-to-Many）
- 多対多（Many-to-Many）

【sql】
-- ユーザーテーブル
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 契約書レビューテーブル（一対多の関係）
CREATE TABLE contract_reviews (
    id SERIAL PRIMARY KEY,
    contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
    reviewer_id INTEGER REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'pending',
    comments TEXT,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
【sql】

## PythonからのSQLクエリ実行

### psycopg2を使用した接続

【python】
import psycopg2
from psycopg2 import sql

# データベース接続
conn = psycopg2.connect(
    host="localhost",
    database="legal_db",
    user="postgres",
    password="password"
)

# カーソルの作成
cur = conn.cursor()

# SQLクエリの実行
cur.execute("SELECT * FROM contracts WHERE status = %s", ('active',))

# 結果の取得
contracts = cur.fetchall()
for contract in contracts:
    print(contract)

# 変更のコミット
conn.commit()

# 接続のクローズ
cur.close()
conn.close()
【python】

### Supabase-pyを使用した接続

【python】
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Supabaseクライアントの初期化
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# データの取得
response = supabase.table('contracts').select('*').execute()
contracts = response.data

# データの挿入
new_contract = {
    'title': '業務委託契約',
    'contract_type': 'service',
    'counterparty': '株式会社ABC',
    'status': 'draft',
    'content': '契約書の内容...'
}
response = supabase.table('contracts').insert(new_contract).execute()

# データの更新
update_data = {'status': 'active'}
response = supabase.table('contracts').update(update_data).eq('id', 1).execute()

# データの削除
response = supabase.table('contracts').delete().eq('id', 1).execute()
【python】

## 認証機能の実装

### ユーザー認証の基本

- サインアップ（ユーザー登録）
- サインイン（ログイン）
- パスワードリセット
- セッション管理

### Supabaseを使用した認証

【python】
# ユーザー登録
response = supabase.auth.sign_up({
    "email": "user@example.com",
    "password": "secure_password"
})

# ログイン
response = supabase.auth.sign_in_with_password({
    "email": "user@example.com",
    "password": "secure_password"
})

# 現在のユーザー情報の取得
user = supabase.auth.get_user()

# ログアウト
supabase.auth.sign_out()

# パスワードリセットメールの送信
supabase.auth.reset_password_email("user@example.com")
【python】

## セキュリティとベストプラクティス

### データベースセキュリティ
- 認証情報の安全な管理
- プリペアドステートメントによるSQLインジェクション対策
- 最小権限の原則

### データ検証
- 入力データのバリデーション
- エラーハンドリング
- トランザクション管理

## 次回予告：Webアプリケーション開発

- Streamlitの基本概念
- インタラクティブなUIの構築
- データの可視化
- デプロイメント 