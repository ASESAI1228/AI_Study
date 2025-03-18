# Webアプリケーション開発

## Streamlitとは

- Pythonベースのデータアプリケーションフレームワーク
- 少ないコードで対話的なWebアプリを構築可能
- データ可視化や機械学習モデルのデモに最適
- デプロイが容易で、迅速なプロトタイピングに適している

## Streamlitの基本構造

【python】
import streamlit as st

# タイトルとヘッダー
st.title("法務文書管理システム")
st.header("契約書一覧")

# サイドバー
st.sidebar.title("メニュー")
option = st.sidebar.selectbox(
    "機能を選択してください",
    ["契約書一覧", "契約書登録", "契約書検索", "分析ダッシュボード"]
)

# テキスト入力
contract_title = st.text_input("契約書タイトル", "")

# 日付選択
effective_date = st.date_input("発効日")

# セレクトボックス
status = st.selectbox(
    "ステータス",
    ["下書き", "レビュー中", "承認済み", "締結済み", "期限切れ"]
)

# ボタン
if st.button("登録"):
    st.success("契約書が登録されました！")
【python】

## データ表示コンポーネント

### テーブル表示

【python】
import pandas as pd

# サンプルデータ
data = {
    "ID": [1, 2, 3, 4],
    "タイトル": ["業務委託契約", "秘密保持契約", "ライセンス契約", "売買契約"],
    "取引先": ["株式会社A", "株式会社B", "株式会社C", "株式会社D"],
    "ステータス": ["締結済み", "レビュー中", "下書き", "承認済み"],
    "発効日": ["2023-01-15", "2023-02-20", "2023-03-10", "2023-04-05"]
}

df = pd.DataFrame(data)

# テーブル表示
st.dataframe(df)

# 静的なテーブル
st.table(df.head(2))
【python】

### グラフ表示

【python】
import matplotlib.pyplot as plt
import numpy as np

# ステータス別の契約書数
status_counts = df["ステータス"].value_counts()

# 棒グラフ
st.bar_chart(status_counts)

# 月別の契約書数（サンプルデータ）
months = ["1月", "2月", "3月", "4月", "5月", "6月"]
contract_counts = [5, 7, 2, 8, 6, 10]

fig, ax = plt.subplots()
ax.plot(months, contract_counts, marker='o')
ax.set_title("月別契約書数")
ax.set_xlabel("月")
ax.set_ylabel("契約書数")

# Matplotlibのグラフを表示
st.pyplot(fig)
【python】

## インタラクティブ要素

### フィルタリングと検索

【python】
# 検索フィルター
search_term = st.text_input("契約書を検索", "")
if search_term:
    filtered_df = df[df["タイトル"].str.contains(search_term) | 
                    df["取引先"].str.contains(search_term)]
    st.dataframe(filtered_df)
else:
    st.dataframe(df)

# 複数選択
selected_statuses = st.multiselect(
    "ステータスでフィルタリング",
    options=df["ステータス"].unique(),
    default=[]
)

if selected_statuses:
    filtered_df = df[df["ステータス"].isin(selected_statuses)]
    st.dataframe(filtered_df)
【python】

### ファイルアップロードと表示

【python】
# ファイルアップロード
uploaded_file = st.file_uploader("契約書をアップロード", type=["pdf", "docx", "txt"])
if uploaded_file is not None:
    # ファイル情報の表示
    file_details = {
        "ファイル名": uploaded_file.name,
        "ファイルタイプ": uploaded_file.type,
        "ファイルサイズ": f"{uploaded_file.size} バイト"
    }
    st.write(file_details)
    
    # テキストファイルの内容を表示
    if uploaded_file.type == "text/plain":
        content = uploaded_file.read().decode("utf-8")
        st.text_area("ファイル内容", content, height=300)
【python】

## データベース連携

【python】
import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# データベース接続情報
conn = psycopg2.connect(
    host=os.getenv("PG_HOST"),
    database=os.getenv("PG_DATABASE"),
    user=os.getenv("PG_USER"),
    password=os.getenv("PG_PASSWORD")
)

# データベースからデータを取得
def get_contracts():
    cur = conn.cursor()
    cur.execute("SELECT id, title, counterparty, status, effective_date FROM contracts")
    rows = cur.fetchall()
    cur.close()
    
    # DataFrameに変換
    df = pd.DataFrame(rows, columns=["ID", "タイトル", "取引先", "ステータス", "発効日"])
    return df

# データの表示
contracts_df = get_contracts()
st.dataframe(contracts_df)
【python】

## AI API連携

【python】
import openai
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# AI分析機能
def analyze_contract(contract_text):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "あなたは法務アシスタントです。契約書を分析し、重要なポイントと潜在的なリスクを特定してください。"},
            {"role": "user", "content": f"以下の契約書を分析してください:\n\n{contract_text}"}
        ],
        max_tokens=500
    )
    return response.choices[0].message.content

# UI部分
st.header("契約書AI分析")
contract_text = st.text_area("分析する契約書のテキストを入力してください", height=300)

if st.button("分析開始"):
    with st.spinner("分析中..."):
        analysis = analyze_contract(contract_text)
    st.subheader("分析結果")
    st.write(analysis)
【python】

## デプロイメント

### ローカル実行

```bash
# アプリケーションの実行
streamlit run app.py
```

### クラウドデプロイ

- Streamlit Cloud
- Heroku
- AWS, GCP, Azure
- Docker + 任意のホスティングサービス

### デプロイ時の注意点

- 環境変数の管理
- APIキーのセキュリティ
- データベース接続の設定
- リソース使用量の最適化

## 次回予告：高度なAI活用とアプリデプロイ研修

- AIコーディング支援ツールの活用
- Docker環境の構築と活用
- RAG（検索拡張生成）の実装
- ファインチューニングの基礎 