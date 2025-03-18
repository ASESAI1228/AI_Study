# データベース操作サンプル

import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta

# .envファイルから環境変数を読み込む
load_dotenv()

# PostgreSQL接続情報
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_DATABASE = os.getenv("PG_DATABASE", "legal_db")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "password")

# Supabase接続情報
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# PostgreSQLに直接接続する関数
def connect_postgres():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        print("PostgreSQLデータベースに接続しました")
        return conn
    except Exception as e:
        print(f"PostgreSQL接続エラー: {e}")
        return None

# Supabaseクライアントを初期化する関数
def init_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Supabase接続情報が設定されていません")
        return None
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabaseクライアントを初期化しました")
        return supabase
    except Exception as e:
        print(f"Supabase初期化エラー: {e}")
        return None

# テーブル作成のサンプル
def create_tables(conn):
    try:
        cur = conn.cursor()
        
        # 契約書テーブルの作成
        cur.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
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
        )
        """)
        
        # 契約書タグテーブルの作成
        cur.execute("""
        CREATE TABLE IF NOT EXISTS contract_tags (
            contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
            tag VARCHAR(50) NOT NULL,
            PRIMARY KEY (contract_id, tag)
        )
        """)
        
        # ユーザーテーブルの作成
        cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            department VARCHAR(100),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 契約書レビューテーブルの作成
        cur.execute("""
        CREATE TABLE IF NOT EXISTS contract_reviews (
            id SERIAL PRIMARY KEY,
            contract_id INTEGER REFERENCES contracts(id) ON DELETE CASCADE,
            reviewer_id INTEGER REFERENCES users(id),
            status VARCHAR(50) DEFAULT 'pending',
            comments TEXT,
            reviewed_at TIMESTAMP WITH TIME ZONE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        print("テーブルを作成しました")
    except Exception as e:
        conn.rollback()
        print(f"テーブル作成エラー: {e}")
    finally:
        cur.close()

# サンプルデータの挿入
def insert_sample_data(conn):
    try:
        cur = conn.cursor()
        
        # ユーザーの挿入
        cur.execute("""
        INSERT INTO users (email, name, department)
        VALUES 
            ('tanaka@example.com', '田中太郎', '法務部'),
            ('yamada@example.com', '山田花子', '法務部'),
            ('suzuki@example.com', '鈴木一郎', '営業部')
        ON CONFLICT (email) DO NOTHING
        """)
        
        # 契約書の挿入
        cur.execute("""
        INSERT INTO contracts (title, contract_type, effective_date, expiration_date, counterparty, status, content)
        VALUES 
            ('業務委託契約', 'service', '2023-01-01', '2023-12-31', '株式会社ABC', 'active', '業務委託契約の内容...'),
            ('秘密保持契約', 'nda', '2023-02-15', '2025-02-14', '株式会社XYZ', 'active', '秘密保持契約の内容...'),
            ('ライセンス契約', 'license', '2023-03-10', '2024-03-09', '株式会社DEF', 'draft', 'ライセンス契約の内容...')
        RETURNING id
        """)
        
        # 挿入された契約書のIDを取得
        contract_ids = [row[0] for row in cur.fetchall()]
        
        # 契約書が挿入されていれば、タグとレビューも挿入
        if contract_ids:
            # タグの挿入
            for contract_id in contract_ids:
                cur.execute("""
                INSERT INTO contract_tags (contract_id, tag)
                VALUES 
                    (%s, 'important'),
                    (%s, 'legal')
                ON CONFLICT DO NOTHING
                """, (contract_id, contract_id))
            
            # レビューの挿入
            cur.execute("""
            INSERT INTO contract_reviews (contract_id, reviewer_id, status, comments, reviewed_at)
            VALUES 
                (%s, 1, 'approved', '問題ありません。', CURRENT_TIMESTAMP),
                (%s, 2, 'pending', NULL, NULL)
            """, (contract_ids[0], contract_ids[1]))
        
        conn.commit()
        print("サンプルデータを挿入しました")
    except Exception as e:
        conn.rollback()
        print(f"データ挿入エラー: {e}")
    finally:
        cur.close()

# 基本的なSELECTクエリ
def basic_select_query(conn):
    try:
        cur = conn.cursor()
        
        print("\n=== アクティブな契約書の一覧 ===")
        cur.execute("SELECT id, title, counterparty, effective_date, expiration_date FROM contracts WHERE status = 'active'")
        contracts = cur.fetchall()
        
        for contract in contracts:
            print(f"ID: {contract[0]}, タイトル: {contract[1]}, 取引先: {contract[2]}, 有効期間: {contract[3]} 〜 {contract[4]}")
        
        print("\n=== 期限が近い契約書 ===")
        thirty_days_later = datetime.now() + timedelta(days=30)
        cur.execute("""
        SELECT id, title, counterparty, expiration_date 
        FROM contracts 
        WHERE expiration_date <= %s AND status = 'active'
        ORDER BY expiration_date
        """, (thirty_days_later.date(),))
        
        expiring_contracts = cur.fetchall()
        for contract in expiring_contracts:
            print(f"ID: {contract[0]}, タイトル: {contract[1]}, 取引先: {contract[2]}, 期限: {contract[3]}")
    except Exception as e:
        print(f"クエリ実行エラー: {e}")
    finally:
        cur.close()

# JOINを使用した複雑なクエリ
def join_query(conn):
    try:
        cur = conn.cursor()
        
        print("\n=== 契約書とレビュー情報 ===")
        cur.execute("""
        SELECT c.id, c.title, c.status, u.name as reviewer, cr.status as review_status, cr.comments
        FROM contracts c
        LEFT JOIN contract_reviews cr ON c.id = cr.contract_id
        LEFT JOIN users u ON cr.reviewer_id = u.id
        ORDER BY c.id
        """)
        
        results = cur.fetchall()
        for row in results:
            print(f"契約書ID: {row[0]}, タイトル: {row[1]}, 状態: {row[2]}, レビュアー: {row[3] or 'なし'}, レビュー状態: {row[4] or 'なし'}")
            if row[5]:
                print(f"  コメント: {row[5]}")
        
        print("\n=== タグ付き契約書 ===")
        cur.execute("""
        SELECT c.id, c.title, string_agg(ct.tag, ', ') as tags
        FROM contracts c
        JOIN contract_tags ct ON c.id = ct.contract_id
        GROUP BY c.id, c.title
        ORDER BY c.id
        """)
        
        tagged_contracts = cur.fetchall()
        for contract in tagged_contracts:
            print(f"ID: {contract[0]}, タイトル: {contract[1]}, タグ: {contract[2]}")
    except Exception as e:
        print(f"JOINクエリ実行エラー: {e}")
    finally:
        cur.close()

# データの更新と削除
def update_and_delete(conn):
    try:
        cur = conn.cursor()
        
        # 更新
        print("\n=== 契約書ステータスの更新 ===")
        cur.execute("""
        UPDATE contracts
        SET status = 'expired', updated_at = CURRENT_TIMESTAMP
        WHERE expiration_date < CURRENT_DATE AND status = 'active'
        RETURNING id, title, status
        """)
        
        updated = cur.fetchall()
        if updated:
            for contract in updated:
                print(f"更新: ID: {contract[0]}, タイトル: {contract[1]}, 新ステータス: {contract[2]}")
        else:
            print("更新対象の契約書はありませんでした")
        
        # 削除（通常は論理削除を推奨）
        print("\n=== 下書き契約書の削除 ===")
        cur.execute("""
        DELETE FROM contracts
        WHERE status = 'draft' AND created_at < CURRENT_TIMESTAMP - INTERVAL '30 days'
        RETURNING id, title
        """)
        
        deleted = cur.fetchall()
        if deleted:
            for contract in deleted:
                print(f"削除: ID: {contract[0]}, タイトル: {contract[1]}")
        else:
            print("削除対象の契約書はありませんでした")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"更新/削除エラー: {e}")
    finally:
        cur.close()

# トランザクションの例
def transaction_example(conn):
    try:
        cur = conn.cursor()
        
        print("\n=== トランザクションの例 ===")
        # トランザクション開始
        cur.execute("BEGIN")
        
        # 新しい契約書の挿入
        cur.execute("""
        INSERT INTO contracts (title, contract_type, effective_date, expiration_date, counterparty, status, content)
        VALUES ('販売代理店契約', 'agency', CURRENT_DATE, CURRENT_DATE + INTERVAL '1 year', '株式会社GHI', 'active', '販売代理店契約の内容...')
        RETURNING id
        """)
        
        contract_id = cur.fetchone()[0]
        print(f"契約書を作成しました（ID: {contract_id}）")
        
        # タグの追加
        cur.execute("""
        INSERT INTO contract_tags (contract_id, tag)
        VALUES (%s, 'sales'), (%s, 'important')
        """, (contract_id, contract_id))
        print("タグを追加しました")
        
        # レビュー依頼の作成
        cur.execute("""
        INSERT INTO contract_reviews (contract_id, reviewer_id, status)
        VALUES (%s, 1, 'pending')
        """, (contract_id,))
        print("レビュー依頼を作成しました")
        
        # トランザクションのコミット
        cur.execute("COMMIT")
        print("トランザクションをコミットしました")
    except Exception as e:
        cur.execute("ROLLBACK")
        print(f"エラーが発生したためロールバックしました: {e}")
    finally:
        cur.close()

# Supabaseを使用したデータ操作
def supabase_operations(supabase):
    if not supabase:
        return
    
    try:
        print("\n=== Supabaseを使用したデータ操作 ===")
        
        # データの取得
        print("契約書データの取得:")
        response = supabase.table('contracts').select('*').limit(5).execute()
        contracts = response.data
        
        for contract in contracts:
            print(f"ID: {contract['id']}, タイトル: {contract['title']}, 状態: {contract['status']}")
        
        # データの挿入
        print("\n新しい契約書の挿入:")
        new_contract = {
            'title': 'システム利用契約',
            'contract_type': 'service',
            'effective_date': datetime.now().strftime('%Y-%m-%d'),
            'expiration_date': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'counterparty': '株式会社JKL',
            'status': 'draft',
            'content': 'システム利用契約の内容...'
        }
        
        response = supabase.table('contracts').insert(new_contract).execute()
        if response.data:
            inserted_id = response.data[0]['id']
            print(f"契約書を挿入しました（ID: {inserted_id}）")
            
            # データの更新
            print("\n契約書の更新:")
            update_data = {'status': 'active'}
            response = supabase.table('contracts').update(update_data).eq('id', inserted_id).execute()
            print(f"契約書を更新しました（ID: {inserted_id}, 新ステータス: active）")
            
            # 関連データの取得（JOIN相当）
            print("\n関連データの取得:")
            response = supabase.table('contracts').select('*, contract_reviews(*)').eq('id', inserted_id).execute()
            if response.data:
                contract = response.data[0]
                print(f"契約書: {contract['title']}")
                if contract['contract_reviews']:
                    for review in contract['contract_reviews']:
                        print(f"  レビューID: {review['id']}, 状態: {review['status']}")
                else:
                    print("  関連するレビューはありません")
    except Exception as e:
        print(f"Supabase操作エラー: {e}")

# Pandas DataFrameとの連携
def pandas_integration(conn):
    try:
        print("\n=== Pandas DataFrameとの連携 ===")
        
        # SQLクエリの結果をDataFrameに読み込む
        query = """
        SELECT c.id, c.title, c.contract_type, c.effective_date, c.expiration_date, 
               c.counterparty, c.status, u.name as reviewer, cr.status as review_status
        FROM contracts c
        LEFT JOIN contract_reviews cr ON c.id = cr.contract_id
        LEFT JOIN users u ON cr.reviewer_id = u.id
        """
        
        df = pd.read_sql_query(query, conn)
        print("契約書データをDataFrameに読み込みました:")
        print(df.head())
        
        # データの分析
        print("\nデータ分析:")
        print(f"契約書の総数: {len(df)}")
        print("\n契約タイプ別の数:")
        print(df['contract_type'].value_counts())
        
        print("\nステータス別の数:")
        print(df['status'].value_counts())
        
        # 有効期限の分析
        df['days_to_expiration'] = (pd.to_datetime(df['expiration_date']) - pd.Timestamp.now()).dt.days
        print("\n期限切れまでの日数の統計:")
        print(df['days_to_expiration'].describe())
        
        # 期限切れが近い契約書
        expiring_soon = df[df['days_to_expiration'].between(0, 30)].sort_values('days_to_expiration')
        print("\n30日以内に期限切れになる契約書:")
        if not expiring_soon.empty:
            for _, row in expiring_soon.iterrows():
                print(f"ID: {row['id']}, タイトル: {row['title']}, 取引先: {row['counterparty']}, 残り日数: {row['days_to_expiration']:.0f}")
        else:
            print("該当する契約書はありません")
    except Exception as e:
        print(f"Pandas連携エラー: {e}")

# メイン処理
if __name__ == "__main__":
    # PostgreSQLに接続
    conn = connect_postgres()
    if conn:
        # テーブルの作成
        create_tables(conn)
        
        # サンプルデータの挿入
        insert_sample_data(conn)
        
        # 基本的なSELECTクエリ
        basic_select_query(conn)
        
        # JOINを使用した複雑なクエリ
        join_query(conn)
        
        # データの更新と削除
        update_and_delete(conn)
        
        # トランザクションの例
        transaction_example(conn)
        
        # Pandas DataFrameとの連携
        pandas_integration(conn)
        
        # 接続のクローズ
        conn.close()
        print("\nPostgreSQLデータベース接続を閉じました")
    
    # Supabaseクライアントの初期化
    supabase = init_supabase()
    if supabase:
        # Supabaseを使用したデータ操作
        supabase_operations(supabase) 