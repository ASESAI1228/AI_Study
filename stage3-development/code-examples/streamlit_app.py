# Streamlitアプリケーションサンプル

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import psycopg2
import os
from dotenv import load_dotenv
import openai
from datetime import datetime, timedelta

# 環境変数の読み込み
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# PostgreSQL接続情報
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_DATABASE = os.getenv("PG_DATABASE", "legal_db")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "password")

# データベース接続
@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            database=PG_DATABASE,
            user=PG_USER,
            password=PG_PASSWORD
        )
        return conn
    except Exception as e:
        st.error(f"データベース接続エラー: {e}")
        return None

# データベースから契約書データを取得
@st.cache_data(ttl=300)
def get_contracts():
    conn = get_db_connection()
    if conn:
        try:
            query = """
            SELECT c.id, c.title, c.contract_type, c.effective_date, c.expiration_date, 
                   c.counterparty, c.status, COUNT(cr.id) as review_count
            FROM contracts c
            LEFT JOIN contract_reviews cr ON c.id = cr.contract_id
            GROUP BY c.id
            ORDER BY c.created_at DESC
            """
            df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            st.error(f"データ取得エラー: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# 契約書タイプ別の統計情報を取得
@st.cache_data(ttl=600)
def get_contract_type_stats():
    conn = get_db_connection()
    if conn:
        try:
            query = """
            SELECT contract_type, COUNT(*) as count,
                   AVG(EXTRACT(DAY FROM (expiration_date - effective_date))) as avg_duration
            FROM contracts
            WHERE effective_date IS NOT NULL AND expiration_date IS NOT NULL
            GROUP BY contract_type
            ORDER BY count DESC
            """
            df = pd.read_sql(query, conn)
            return df
        except Exception as e:
            st.error(f"統計情報取得エラー: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# 月別の契約書数を取得
@st.cache_data(ttl=600)
def get_monthly_stats():
    conn = get_db_connection()
    if conn:
        try:
            query = """
            SELECT DATE_TRUNC('month', effective_date) as month, COUNT(*) as count
            FROM contracts
            WHERE effective_date IS NOT NULL
            GROUP BY month
            ORDER BY month
            """
            df = pd.read_sql(query, conn)
            df['month'] = pd.to_datetime(df['month']).dt.strftime('%Y-%m')
            return df
        except Exception as e:
            st.error(f"月別統計取得エラー: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# 契約書を登録する関数
def register_contract(title, contract_type, counterparty, effective_date, expiration_date, status, content):
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            query = """
            INSERT INTO contracts (title, contract_type, counterparty, effective_date, expiration_date, status, content)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            cur.execute(query, (title, contract_type, counterparty, effective_date, expiration_date, status, content))
            contract_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            return contract_id
        except Exception as e:
            conn.rollback()
            st.error(f"契約書登録エラー: {e}")
            return None
    return None

# 契約書を分析する関数
def analyze_contract(contract_text):
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは法務アシスタントです。契約書を分析し、重要なポイントと潜在的なリスクを特定してください。"},
                {"role": "user", "content": f"以下の契約書を分析してください:\n\n{contract_text}"}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"AI分析エラー: {e}")
        return "分析中にエラーが発生しました。"

# アプリケーションのメイン部分
def main():
    st.set_page_config(
        page_title="法務文書管理システム",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("法務文書管理システム")
    
    # サイドバーメニュー
    st.sidebar.title("メニュー")
    menu = st.sidebar.radio(
        "機能を選択してください",
        ["契約書一覧", "契約書登録", "契約書検索", "分析ダッシュボード", "AI分析"]
    )
    
    # 契約書一覧
    if menu == "契約書一覧":
        st.header("契約書一覧")
        
        contracts_df = get_contracts()
        if not contracts_df.empty:
            # 日付列の整形
            if 'effective_date' in contracts_df.columns:
                contracts_df['effective_date'] = pd.to_datetime(contracts_df['effective_date']).dt.strftime('%Y-%m-%d')
            if 'expiration_date' in contracts_df.columns:
                contracts_df['expiration_date'] = pd.to_datetime(contracts_df['expiration_date']).dt.strftime('%Y-%m-%d')
            
            # データフレームの表示
            st.dataframe(contracts_df)
            
            # 期限切れが近い契約書の警告
            today = datetime.now().date()
            expiring_soon = contracts_df[
                (pd.to_datetime(contracts_df['expiration_date']) - pd.Timedelta(days=30)).dt.date <= today
            ]
            
            if not expiring_soon.empty:
                st.warning(f"⚠️ {len(expiring_soon)}件の契約書が30日以内に期限切れになります")
                st.dataframe(expiring_soon)
        else:
            st.info("契約書データがありません。「契約書登録」から新しい契約書を追加してください。")
    
    # 契約書登録
    elif menu == "契約書登録":
        st.header("契約書登録")
        
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("契約書タイトル", "")
            contract_type = st.selectbox(
                "契約書タイプ",
                ["業務委託契約", "秘密保持契約", "ライセンス契約", "売買契約", "雇用契約", "その他"]
            )
            counterparty = st.text_input("取引先", "")
            
        with col2:
            effective_date = st.date_input("発効日")
            expiration_date = st.date_input("有効期限", value=effective_date + timedelta(days=365))
            status = st.selectbox(
                "ステータス",
                ["下書き", "レビュー中", "承認済み", "締結済み", "期限切れ"]
            )
        
        content = st.text_area("契約書の内容", height=300)
        
        if st.button("契約書を登録"):
            if title and counterparty and content:
                contract_id = register_contract(
                    title, contract_type, counterparty, 
                    effective_date, expiration_date, status, content
                )
                
                if contract_id:
                    st.success(f"契約書が正常に登録されました（ID: {contract_id}）")
                    # キャッシュをクリアして最新データを表示
                    get_contracts.clear()
                    get_contract_type_stats.clear()
                    get_monthly_stats.clear()
                else:
                    st.error("契約書の登録に失敗しました。")
            else:
                st.warning("タイトル、取引先、契約書の内容は必須項目です。")
    
    # 契約書検索
    elif menu == "契約書検索":
        st.header("契約書検索")
        
        # 検索オプション
        search_term = st.text_input("検索キーワード", "")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            date_filter = st.checkbox("日付でフィルタリング")
        with col2:
            if date_filter:
                start_date = st.date_input("開始日")
        with col3:
            if date_filter:
                end_date = st.date_input("終了日")
        
        if st.button("検索") or search_term:
            # データの取得
            contracts_df = get_contracts()
            
            if not contracts_df.empty:
                # 検索条件の適用
                if search_term:
                    # タイトル、取引先、契約書タイプで検索
                    filtered_df = contracts_df[
                        contracts_df["title"].str.contains(search_term, case=False) |
                        contracts_df["counterparty"].str.contains(search_term, case=False) |
                        contracts_df["contract_type"].str.contains(search_term, case=False)
                    ]
                else:
                    filtered_df = contracts_df
                
                # 日付フィルタリング
                if date_filter:
                    filtered_df = filtered_df[
                        (filtered_df["effective_date"] >= start_date) &
                        (filtered_df["effective_date"] <= end_date)
                    ]
                
                # 結果の表示
                if not filtered_df.empty:
                    st.write(f"{len(filtered_df)}件の契約書が見つかりました")
                    st.dataframe(filtered_df)
                else:
                    st.info("条件に一致する契約書はありません")
            else:
                st.info("契約書データがありません")
    
    # 分析ダッシュボード
    elif menu == "分析ダッシュボード":
        st.header("契約書分析ダッシュボード")
        
        # 契約書タイプ別の統計
        st.subheader("契約書タイプ別の統計")
        type_stats = get_contract_type_stats()
        
        if not type_stats.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # 契約書タイプ別の件数
                fig1, ax1 = plt.subplots(figsize=(10, 6))
                ax1.bar(type_stats['contract_type'], type_stats['count'])
                ax1.set_title("契約書タイプ別の件数")
                ax1.set_xlabel("契約書タイプ")
                ax1.set_ylabel("件数")
                plt.xticks(rotation=45)
                st.pyplot(fig1)
            
            with col2:
                # 契約書タイプ別の平均契約期間
                fig2, ax2 = plt.subplots(figsize=(10, 6))
                ax2.bar(type_stats['contract_type'], type_stats['avg_duration'])
                ax2.set_title("契約書タイプ別の平均契約期間（日）")
                ax2.set_xlabel("契約書タイプ")
                ax2.set_ylabel("平均日数")
                plt.xticks(rotation=45)
                st.pyplot(fig2)
            
            # データテーブルの表示
            st.dataframe(type_stats)
        else:
            st.info("統計データがありません")
        
        # 月別の契約書数の推移
        st.subheader("月別の契約書数の推移")
        monthly_stats = get_monthly_stats()
        
        if not monthly_stats.empty:
            fig3, ax3 = plt.subplots(figsize=(12, 6))
            ax3.plot(monthly_stats['month'], monthly_stats['count'], marker='o')
            ax3.set_title("月別の契約書数")
            ax3.set_xlabel("月")
            ax3.set_ylabel("契約書数")
            plt.xticks(rotation=45)
            st.pyplot(fig3)
            
            # データテーブルの表示
            st.dataframe(monthly_stats)
        else:
            st.info("月別統計データがありません")
    
    # AI分析
    elif menu == "AI分析":
        st.header("契約書AI分析")
        
        # 分析方法の選択
        analysis_method = st.radio(
            "分析方法を選択してください",
            ["テキスト入力", "データベースから選択"]
        )
        
        if analysis_method == "テキスト入力":
            contract_text = st.text_area("分析する契約書のテキストを入力してください", height=300)
            
            if st.button("分析開始") and contract_text:
                with st.spinner("契約書を分析中..."):
                    analysis_result = analyze_contract(contract_text)
                
                st.subheader("分析結果")
                st.write(analysis_result)
        
        else:  # データベースから選択
            contracts_df = get_contracts()
            
            if not contracts_df.empty:
                selected_contract_id = st.selectbox(
                    "分析する契約書を選択してください",
                    contracts_df['id'].tolist(),
                    format_func=lambda x: contracts_df.loc[contracts_df['id'] == x, 'title'].iloc[0]
                )
                
                # 選択された契約書の内容を取得
                conn = get_db_connection()
                if conn:
                    try:
                        query = "SELECT content FROM contracts WHERE id = %s"
                        cur = conn.cursor()
                        cur.execute(query, (selected_contract_id,))
                        content = cur.fetchone()[0]
                        cur.close()
                        
                        if content:
                            st.text_area("契約書の内容", content, height=200)
                            
                            if st.button("分析開始"):
                                with st.spinner("契約書を分析中..."):
                                    analysis_result = analyze_contract(content)
                                
                                st.subheader("分析結果")
                                st.write(analysis_result)
                        else:
                            st.warning("選択された契約書には内容がありません")
                    except Exception as e:
                        st.error(f"契約書内容の取得エラー: {e}")
            else:
                st.info("契約書データがありません")

if __name__ == "__main__":
    main() 