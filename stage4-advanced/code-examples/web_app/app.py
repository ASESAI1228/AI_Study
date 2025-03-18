# Streamlitを使用した法務AIアプリケーション

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import openai
from dotenv import load_dotenv
import tempfile
import PyPDF2
import re
from io import BytesIO

# 環境変数の読み込み
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# データベース接続設定
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "legaldb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")
DB_PORT = os.getenv("DB_PORT", "5432")

# データベース接続
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        st.error(f"データベース接続エラー: {e}")
        return None

# PDFからテキストを抽出
def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    for page_num in range(len(pdf_reader.pages)):
        text += pdf_reader.pages[page_num].extract_text()
    return text

# 契約書の分析
def analyze_contract(contract_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたは法務専門家です。契約書を分析し、重要なポイントとリスクを特定してください。"},
                {"role": "user", "content": f"以下の契約書を分析し、重要なポイント、潜在的なリスク、改善提案を箇条書きでまとめてください。\n\n{contract_text}"}
            ],
            temperature=0.2,
            max_tokens=1500
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"分析中にエラーが発生しました: {e}"

# 契約書の保存
def save_contract(title, contract_type_id, counterparty_id, status, effective_date, expiration_date, content):
    conn = get_db_connection()
    if not conn:
        return False, "データベース接続エラー"
    
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO contracts (title, contract_type_id, counterparty_id, status, effective_date, expiration_date, content)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (title, contract_type_id, counterparty_id, status, effective_date, expiration_date, content)
            )
            contract_id = cur.fetchone()['id']
            conn.commit()
            return True, contract_id
    except Exception as e:
        conn.rollback()
        return False, f"保存中にエラーが発生しました: {e}"
    finally:
        conn.close()

# 契約書の検索
def search_contracts(keyword, contract_type_id, status):
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        with conn.cursor() as cur:
            query = """
                SELECT c.id, c.title, c.status, c.effective_date, c.expiration_date, 
                       ct.name as contract_type, cp.name as counterparty
                FROM contracts c
                JOIN contract_types ct ON c.contract_type_id = ct.id
                JOIN counterparties cp ON c.counterparty_id = cp.id
                WHERE 1=1
            """
            params = []
            
            if keyword:
                query += " AND (c.title ILIKE %s OR c.content ILIKE %s)"
                keyword_param = f"%{keyword}%"
                params.extend([keyword_param, keyword_param])
            
            if contract_type_id:
                query += " AND c.contract_type_id = %s"
                params.append(contract_type_id)
            
            if status:
                query += " AND c.status = %s"
                params.append(status)
            
            query += " ORDER BY c.updated_at DESC"
            
            cur.execute(query, params)
            return cur.fetchall()
    except Exception as e:
        st.error(f"検索中にエラーが発生しました: {e}")
        return []
    finally:
        conn.close()

# 契約書の生成
def generate_contract(template_type, variables):
    try:
        # 変数をJSON形式に変換
        variables_json = json.dumps(variables, ensure_ascii=False)
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたは法務専門家です。提供された情報に基づいて契約書を生成してください。"},
                {"role": "user", "content": f"以下の情報に基づいて{template_type}を生成してください。\n\n変数: {variables_json}"}
            ],
            temperature=0.2,
            max_tokens=2000
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"生成中にエラーが発生しました: {e}"

# 法的質問への回答
def answer_legal_question(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "あなたは法務専門家です。法的な質問に対して正確で実用的な回答を提供してください。"},
                {"role": "user", "content": question}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"回答生成中にエラーが発生しました: {e}"

# アプリケーションのUI
def main():
    st.set_page_config(
        page_title="法務AIアシスタント",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("法務AIアシスタント")
    
    # サイドバーメニュー
    menu = st.sidebar.selectbox(
        "機能を選択",
        ["ホーム", "契約書分析", "契約書管理", "契約書生成", "契約書検索", "統計ダッシュボード"]
    )
    
    # ホーム画面
    if menu == "ホーム":
        st.header("法務業務のAI支援ツール")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("主な機能")
            st.markdown("""
            - **契約書分析**: PDFやテキスト形式の契約書を分析し、重要ポイントとリスクを特定
            - **契約書管理**: 契約書の保存、更新、ステータス管理
            - **契約書生成**: テンプレートベースの契約書自動生成
            - **契約書検索**: キーワードや条件による契約書の検索
            - **統計ダッシュボード**: 契約書データの可視化と分析
            """)
        
        with col2:
            st.subheader("最近の活動")
            # 最近の契約書を表示（実際のアプリではデータベースから取得）
            recent_contracts = search_contracts("", None, None)[:5]
            if recent_contracts:
                for contract in recent_contracts:
                    st.markdown(f"**{contract['title']}** - {contract['status']} ({contract['contract_type']})")
            else:
                st.info("最近の契約書はありません")
    
    # 契約書分析
    elif menu == "契約書分析":
        st.header("契約書分析")
        
        upload_tab, text_tab = st.tabs(["ファイルアップロード", "テキスト入力"])
        
        with upload_tab:
            uploaded_file = st.file_uploader("契約書をアップロード (PDF)", type=["pdf"])
            
            if uploaded_file:
                with st.spinner("PDFを処理中..."):
                    contract_text = extract_text_from_pdf(uploaded_file)
                    st.session_state.contract_text = contract_text
                
                st.subheader("抽出されたテキスト")
                with st.expander("テキストを表示"):
                    st.text_area("契約書テキスト", contract_text, height=200)
                
                if st.button("分析を実行"):
                    with st.spinner("契約書を分析中..."):
                        analysis = analyze_contract(contract_text)
                    
                    st.subheader("分析結果")
                    st.markdown(analysis)
                    
                    # 分析結果の保存オプション
                    if st.button("この契約書と分析結果を保存"):
                        st.session_state.save_contract = True
                        st.session_state.contract_text = contract_text
                        st.session_state.analysis = analysis
                        st.experimental_rerun()
        
        with text_tab:
            contract_text = st.text_area("契約書テキストを入力", height=300)
            
            if st.button("テキストを分析") and contract_text:
                with st.spinner("契約書を分析中..."):
                    analysis = analyze_contract(contract_text)
                
                st.subheader("分析結果")
                st.markdown(analysis)
                
                # 分析結果の保存オプション
                if st.button("この契約書と分析結果を保存"):
                    st.session_state.save_contract = True
                    st.session_state.contract_text = contract_text
                    st.session_state.analysis = analysis
                    st.experimental_rerun()
    
    # 契約書管理
    elif menu == "契約書管理":
        st.header("契約書管理")
        
        # 契約書の保存フォーム（分析画面からの遷移）
        if hasattr(st.session_state, 'save_contract') and st.session_state.save_contract:
            st.subheader("契約書の保存")
            
            # 契約タイプとカウンターパーティの取得（実際のアプリではDBから取得）
            contract_types = [{"id": 1, "name": "秘密保持契約"}, {"id": 2, "name": "業務委託契約"}]
            counterparties = [{"id": 1, "name": "株式会社テックイノベーション"}, {"id": 2, "name": "株式会社法務パートナーズ"}]
            
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("契約書タイトル")
                contract_type_id = st.selectbox("契約書タイプ", options=[c["id"] for c in contract_types], format_func=lambda x: next((c["name"] for c in contract_types if c["id"] == x), ""))
                counterparty_id = st.selectbox("取引先", options=[c["id"] for c in counterparties], format_func=lambda x: next((c["name"] for c in counterparties if c["id"] == x), ""))
                status = st.selectbox("ステータス", ["下書き", "レビュー中", "締結済み", "期限切れ", "終了"])
            
            with col2:
                effective_date = st.date_input("発効日")
                expiration_date = st.date_input("満了日")
            
            if st.button("保存"):
                success, result = save_contract(
                    title, contract_type_id, counterparty_id, status,
                    effective_date, expiration_date, st.session_state.contract_text
                )
                
                if success:
                    st.success(f"契約書が保存されました (ID: {result})")
                    # セッション状態をクリア
                    del st.session_state.save_contract
                    del st.session_state.contract_text
                    if hasattr(st.session_state, 'analysis'):
                        del st.session_state.analysis
                else:
                    st.error(result)
        
        # 契約書一覧
        st.subheader("契約書一覧")
        
        # 検索フィルター
        col1, col2, col3 = st.columns(3)
        with col1:
            search_keyword = st.text_input("キーワード検索")
        with col2:
            # 契約タイプの取得（実際のアプリではDBから取得）
            contract_types = [{"id": 1, "name": "秘密保持契約"}, {"id": 2, "name": "業務委託契約"}]
            search_type = st.selectbox(
                "契約書タイプ", 
                options=[None] + [c["id"] for c in contract_types],
                format_func=lambda x: "すべて" if x is None else next((c["name"] for c in contract_types if c["id"] == x), "")
            )
        with col3:
            search_status = st.selectbox("ステータス", [None, "下書き", "レビュー中", "締結済み", "期限切れ", "終了"], format_func=lambda x: "すべて" if x is None else x)
        
        if st.button("検索"):
            contracts = search_contracts(search_keyword, search_type, search_status)
            
            if contracts:
                st.dataframe(
                    pd.DataFrame(contracts),
                    column_config={
                        "id": "ID",
                        "title": "タイトル",
                        "contract_type": "契約書タイプ",
                        "counterparty": "取引先",
                        "status": "ステータス",
                        "effective_date": "発効日",
                        "expiration_date": "満了日"
                    },
                    use_container_width=True
                )
            else:
                st.info("条件に一致する契約書はありません")
    
    # 契約書生成
    elif menu == "契約書生成":
        st.header("契約書生成")
        
        # テンプレート選択
        template_type = st.selectbox(
            "契約書タイプを選択",
            ["秘密保持契約書", "業務委託契約書", "雇用契約書", "賃貸借契約書"]
        )
        
        # テンプレート変数の入力
        st.subheader("契約内容の入力")
        
        if template_type == "秘密保持契約書":
            col1, col2 = st.columns(2)
            with col1:
                company1 = st.text_input("甲の会社名")
                company1_address = st.text_input("甲の住所")
                company1_rep = st.text_input("甲の代表者名")
            with col2:
                company2 = st.text_input("乙の会社名")
                company2_address = st.text_input("乙の住所")
                company2_rep = st.text_input("乙の代表者名")
            
            term = st.number_input("秘密保持期間（年）", min_value=1, max_value=10, value=3)
            purpose = st.text_input("目的", "業務提携の検討")
            
            variables = {
                "company1": company1,
                "company1_address": company1_address,
                "company1_rep": company1_rep,
                "company2": company2,
                "company2_address": company2_address,
                "company2_rep": company2_rep,
                "term": term,
                "purpose": purpose
            }
        
        elif template_type == "業務委託契約書":
            col1, col2 = st.columns(2)
            with col1:
                client = st.text_input("委託者名")
                client_address = st.text_input("委託者住所")
                client_rep = st.text_input("委託者代表者名")
            with col2:
                contractor = st.text_input("受託者名")
                contractor_address = st.text_input("受託者住所")
                contractor_rep = st.text_input("受託者代表者名")
            
            service = st.text_area("委託業務内容")
            fee = st.text_input("委託料")
            payment_terms = st.text_input("支払条件", "毎月末締め翌月末払い")
            
            variables = {
                "client": client,
                "client_address": client_address,
                "client_rep": client_rep,
                "contractor": contractor,
                "contractor_address": contractor_address,
                "contractor_rep": contractor_rep,
                "service": service,
                "fee": fee,
                "payment_terms": payment_terms
            }
        
        else:
            st.info("このテンプレートタイプの入力フォームはまだ実装されていません。")
            variables = {}
        
        # 契約書生成
        if st.button("契約書を生成") and variables:
            with st.spinner("契約書を生成中..."):
                generated_contract = generate_contract(template_type, variables)
            
            st.subheader("生成された契約書")
            st.text_area("契約書テキスト", generated_contract, height=400)
            
            # ダウンロードボタン
            download_button = st.download_button(
                label="契約書をダウンロード",
                data=generated_contract,
                file_name=f"{template_type}_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    # 統計ダッシュボード
    elif menu == "統計ダッシュボード":
        st.header("統計ダッシュボード")
        
        # サンプルデータ（実際のアプリではDBから取得）
        contract_types_data = {
            "秘密保持契約": 15,
            "業務委託契約": 8,
            "ライセンス契約": 5,
            "雇用契約": 12,
            "賃貸借契約": 3
        }
        
        status_data = {
            "下書き": 10,
            "レビュー中": 8,
            "締結済み": 20,
            "期限切れ": 3,
            "終了": 2
        }
        
        monthly_data = {
            "2023-01": 3,
            "2023-02": 5,
            "2023-03": 2,
            "2023-04": 7,
            "2023-05": 4,
            "2023-06": 8
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("契約書タイプ別件数")
            fig, ax = plt.subplots()
            ax.pie(
                contract_types_data.values(),
                labels=contract_types_data.keys(),
                autopct='%1.1f%%',
                startangle=90
            )
            ax.axis('equal')
            st.pyplot(fig)
        
        with col2:
            st.subheader("ステータス別件数")
            fig, ax = plt.subplots()
            ax.bar(
                status_data.keys(),
                status_data.values(),
                color='skyblue'
            )
            plt.xticks(rotation=45)
            st.pyplot(fig)
        
        st.subheader("月別契約書作成数")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(
            list(monthly_data.keys()),
            list(monthly_data.values()),
            marker='o',
            linestyle='-',
            color='green'
        )
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)

# アプリケーションの実行
if __name__ == "__main__":
    main() 