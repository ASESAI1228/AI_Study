# Python基礎演習

## 目的

この演習では、Pythonの基本的な構文と機能を実践的に学びます。法務業務で役立つテキスト処理やファイル操作を中心に演習を行います。

## 準備

1. Pythonがインストールされていることを確認してください
2. Visual Studio Codeなどのコードエディタを準備してください
3. 演習用のフォルダを作成し、そこで作業を行ってください

## 演習1：基本的なデータ型と操作

### 課題1-1：変数と基本データ型

以下のコードを`data_types.py`というファイル名で保存し、実行してください：

【python】
# 基本的なデータ型の練習

# 1. 以下の変数を定義してください
# - あなたの名前を格納する変数 name
# - あなたの年齢を格納する変数 age
# - あなたが法務担当者かどうかを格納する変数 is_legal_staff
name = "山田太郎"  # あなたの名前に変更してください
age = 30  # あなたの年齢に変更してください
is_legal_staff = True  # あなたが法務担当者ならTrue、そうでなければFalse

# 2. 上記の変数を使って、以下のフォーマットで自己紹介文を作成し、表示してください
# "私の名前は[名前]です。年齢は[年齢]歳で、法務担当者です。" または
# "私の名前は[名前]です。年齢は[年齢]歳で、法務担当者ではありません。"
legal_status = "法務担当者です" if is_legal_staff else "法務担当者ではありません"
introduction = f"私の名前は{name}です。年齢は{age}歳で、{legal_status}。"
print(introduction)

# 3. 以下の法務関連の情報を辞書として定義してください
# - 契約書の種類のリスト
# - 各契約書の重要度（1〜5の整数）
# - 担当者の名前
contract_info = {
    "contract_types": ["売買契約", "賃貸借契約", "業務委託契約", "雇用契約", "NDA"],
    "importance": {
        "売買契約": 5,
        "賃貸借契約": 4,
        "業務委託契約": 4,
        "雇用契約": 5,
        "NDA": 3
    },
    "manager": "法務太郎"
}

# 4. 上記の辞書から、最も重要度の高い契約書の種類を抽出して表示してください
most_important = max(contract_info["importance"].items(), key=lambda x: x[1])
print(f"最も重要度の高い契約書は{most_important[0]}（重要度: {most_important[1]}）です")

# 5. 契約書の種類のリストに「ライセンス契約」を追加し、重要度を4として登録してください
contract_info["contract_types"].append("ライセンス契約")
contract_info["importance"]["ライセンス契約"] = 4
print(f"更新後の契約書リスト: {contract_info['contract_types']}")
print(f"ライセンス契約の重要度: {contract_info['importance']['ライセンス契約']}")
【python】


### 課題1-2：条件分岐とループ

以下のコードを`control_flow.py`というファイル名で保存し、実行してください：

【python】
# 条件分岐とループの練習

# 1. 以下の契約書リストを定義してください
contracts = [
    {"name": "売買契約A", "status": "審査中", "deadline": "2023-06-15", "importance": 4},
    {"name": "業務委託契約B", "status": "承認済", "deadline": "2023-06-10", "importance": 3},
    {"name": "NDA", "status": "締結済", "deadline": "2023-05-28", "importance": 2},
    {"name": "ライセンス契約C", "status": "審査中", "deadline": "2023-06-20", "importance": 5},
    {"name": "雇用契約D", "status": "差戻", "deadline": "2023-06-05", "importance": 4}
]

# 2. 重要度が4以上の契約書のみを抽出し、名前と重要度を表示してください
print("重要度が高い契約書:")
for contract in contracts:
    if contract["importance"] >= 4:
        print(f"- {contract['name']} (重要度: {contract['importance']})")

# 3. ステータスが「審査中」の契約書の数を数えて表示してください
review_count = sum(1 for contract in contracts if contract["status"] == "審査中")
print(f"\n審査中の契約書数: {review_count}")

# 4. 締切日が直近の契約書を特定し、その名前と締切日を表示してください
# ヒント: 締切日の文字列を日付オブジェクトに変換すると比較しやすくなります
import datetime

# 文字列を日付オブジェクトに変換する関数
def str_to_date(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

# 各契約書に日付オブジェクトを追加
for contract in contracts:
    contract["deadline_date"] = str_to_date(contract["deadline"])

# 現在の日付を取得
today = datetime.date.today()

# 締切日が現在より後で、最も近い契約書を見つける
upcoming_contracts = [c for c in contracts if c["deadline_date"] >= today]
if upcoming_contracts:
    closest_contract = min(upcoming_contracts, key=lambda x: x["deadline_date"])
    print(f"\n最も締切が近い契約書: {closest_contract['name']} (締切: {closest_contract['deadline']})")
else:
    print("\n締切が近い契約書はありません")

# 5. 契約書を重要度の高い順にソートし、名前、ステータス、重要度を表示してください
sorted_contracts = sorted(contracts, key=lambda x: x["importance"], reverse=True)
print("\n重要度順の契約書リスト:")
for contract in sorted_contracts:
    print(f"- {contract['name']} (ステータス: {contract['status']}, 重要度: {contract['importance']})")
【python】

## 演習2：テキスト処理

### 課題2-1：文字列操作

以下のコードを`text_processing.py`というファイル名で保存し、実行してください：

【python】
# テキスト処理の練習

# 1. 以下の契約書条項を定義してください
clause = """
第10条（秘密保持）
1. 甲および乙は、本契約に関連して知り得た相手方の技術上・営業上の一切の情報（以下「秘密情報」という）を、相手方の事前の書面による承諾なく第三者に開示または漏洩してはならない。
2. 前項の規定にかかわらず、次の各号のいずれかに該当する情報については、秘密情報から除外するものとする。
   (1) 開示を受けた際、既に公知となっていた情報
   (2) 開示を受けた際、既に自己が保有していた情報
   (3) 開示を受けた後、自己の責によらず公知となった情報
   (4) 正当な権限を有する第三者から適法に取得した情報
   (5) 相手方から開示された情報によらず、独自に開発した情報
3. 本条の規定は、本契約終了後も3年間効力を有するものとする。
"""

# 2. 上記の条項から、以下の情報を抽出して表示してください
# - 条項のタイトル
# - 秘密情報の定義
# - 秘密情報から除外される項目のリスト
# - 秘密保持義務の有効期間

import re

# タイトルの抽出
title_match = re.search(r"第\d+条（(.+?)）", clause)
if title_match:
    title = title_match.group(1)
    print(f"条項のタイトル: {title}")

# 秘密情報の定義を抽出
definition_match = re.search(r"「秘密情報」という\）(.+?)を", clause)
if definition_match:
    definition = definition_match.group(1).strip()
    print(f"秘密情報の定義: {definition}")

# 除外項目を抽出
exclusions = re.findall(r"\(\d+\) (.+?)$", clause, re.MULTILINE)
print("\n秘密情報から除外される項目:")
for item in exclusions:
    print(f"- {item}")

# 有効期間を抽出
period_match = re.search(r"本契約終了後も(\d+)年間", clause)
if period_match:
    period = period_match.group(1)
    print(f"\n秘密保持義務の有効期間: {period}年間")

# 3. 上記の条項を、以下のように修正してください
# - 「甲および乙」を「甲、乙および丙」に変更
# - 有効期間を3年から5年に変更
modified_clause = clause.replace("甲および乙", "甲、乙および丙")
modified_clause = re.sub(r"本契約終了後も3年間", "本契約終了後も5年間", modified_clause)

print("\n修正後の条項:")
print(modified_clause)

# 4. 修正後の条項の単語数をカウントして表示してください
words = re.findall(r'\w+', modified_clause)
print(f"\n修正後の条項の単語数: {len(words)}")
【python】

### 課題2-2：ファイル操作

以下のコードを`file_operations.py`というファイル名で保存し、実行してください：

【python】
# ファイル操作の練習

# 1. 以下の契約書テンプレートを作成し、ファイルに保存してください
contract_template = """
業務委託契約書

株式会社〇〇（以下「甲」という）と株式会社△△（以下「乙」という）は、以下のとおり業務委託契約（以下「本契約」という）を締結する。

第1条（目的）
甲は、以下に定める業務（以下「本業務」という）を乙に委託し、乙はこれを受託する。
業務内容：[業務内容]

第2条（委託料）
1. 本業務の委託料は、月額金[委託料]円（税別）とする。
2. 甲は、前項の委託料を、乙の請求に基づき、請求書受領月の翌月末日までに乙の指定する銀行口座に振り込む方法により支払うものとする。
3. 振込手数料は甲の負担とする。

第3条（契約期間）
1. 本契約の有効期間は、[開始日]から[終了日]までとする。
2. 前項の期間満了の1ヶ月前までに、甲または乙から相手方に対して書面による契約終了の意思表示がない場合、本契約は同一条件でさらに1年間自動的に更新されるものとし、以後も同様とする。

第4条（秘密保持）
甲および乙は、本契約に関連して知り得た相手方の技術上・営業上の一切の情報を、相手方の事前の書面による承諾なく第三者に開示または漏洩してはならない。

以上、本契約の成立を証するため、本書2通を作成し、甲乙記名押印のうえ、各1通を保有する。

[契約締結日]

甲：[甲の住所]
  [甲の名称]
  [甲の代表者]  印

乙：[乙の住所]
  [乙の名称]
  [乙の代表者]  印
"""

# ファイルに書き込み
with open("contract_template.txt", "w", encoding="utf-8") as f:
    f.write(contract_template)

print("契約書テンプレートをファイルに保存しました。")

# 2. 上記のテンプレートを読み込み、以下の情報で置換して新しい契約書を作成してください
contract_info = {
    "[業務内容]": "法務文書の作成支援および契約書レビュー業務",
    "[委託料]": "300,000",
    "[開始日]": "2023年7月1日",
    "[終了日]": "2024年6月30日",
    "[契約締結日]": "2023年6月15日",
    "[甲の住所]": "東京都千代田区丸の内1-1-1",
    "[甲の名称]": "株式会社法務テック",
    "[甲の代表者]": "代表取締役 法務太郎",
    "[乙の住所]": "東京都港区赤坂2-2-2",
    "[乙の名称]": "リーガルサポート株式会社",
    "[乙の代表者]": "代表取締役 契約花子"
}

# テンプレートを読み込み
with open("contract_template.txt", "r", encoding="utf-8") as f:
    template_content = f.read()

# 情報を置換
new_contract = template_content
for key, value in contract_info.items():
    new_contract = new_contract.replace(key, value)

# 新しい契約書をファイルに保存
with open("new_contract.txt", "w", encoding="utf-8") as f:
    f.write(new_contract)

print("新しい契約書を作成しました。")

# 3. 作成した契約書から特定の条項（第4条）を抽出して表示してください
with open("new_contract.txt", "r", encoding="utf-8") as f:
    contract_content = f.read()

# 正規表現で第4条を抽出
import re
article4_match = re.search(r"第4条（.+?）\n(.+?)(?=\n\n)", contract_content, re.DOTALL)
if article4_match:
    article4 = article4_match.group(0)
    print("\n第4条（秘密保持）:")
    print(article4)
else:
    print("\n第4条が見つかりませんでした。")
【python】

## 演習3：APIとの連携

### 課題3-1：外部APIの利用

以下のコードを`api_client.py`というファイル名で保存し、実行してください：

【python】
# 外部APIとの連携練習

# 注意: 以下のコードを実行するには、requestsパッケージのインストールが必要です
# pip install requests

import requests
import json

# 1. 公開APIを使って法律関連の情報を取得する
# 例として、JSONPlaceholderの投稿データを「法的アドバイス」とみなして取得します
def get_legal_advice():
    url = "https://jsonplaceholder.typicode.com/posts"
    response = requests.get(url)
    
    if response.status_code == 200:
        # 最初の5件を「法的アドバイス」として扱う
        posts = response.json()[:5]
        print("法的アドバイス一覧:")
        for post in posts:
            print(f"タイトル: {post['title']}")
            print(f"内容: {post['body']}")
            print("-" * 50)
        return posts
    else:
        print(f"エラー: {response.status_code}")
        return None

# 2. 取得したデータをJSONファイルとして保存する
def save_to_json(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"データを{filename}に保存しました。")

# 3. 保存したJSONファイルを読み込み、データを加工する
def process_legal_advice(filename):
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # データを加工（各アドバイスに重要度と分野を追加）
    categories = ["契約法", "知的財産権", "労働法", "会社法", "個人情報保護"]
    for i, item in enumerate(data):
        item["importance"] = i % 3 + 1  # 重要度を1-3でランダムに設定
        item["category"] = categories[i % len(categories)]  # 分野をランダムに設定
    
    # 加工したデータを新しいファイルに保存
    with open("processed_" + filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print("データを加工し、新しいファイルに保存しました。")
    return data

# 4. 加工したデータを分析する
def analyze_legal_advice(data):
    # カテゴリ別の件数をカウント
    category_count = {}
    for item in data:
        category = item["category"]
        if category in category_count:
            category_count[category] += 1
        else:
            category_count[category] = 1
    
    print("\n分野別アドバイス件数:")
    for category, count in category_count.items():
        print(f"{category}: {count}件")
    
    # 重要度の高いアドバイスを抽出
    important_advice = [item for item in data if item["importance"] >= 3]
    print(f"\n重要度の高いアドバイス: {len(important_advice)}件")
    for advice in important_advice:
        print(f"タイトル: {advice['title']} (分野: {advice['category']})")

# メイン処理
if __name__ == "__main__":
    # 1. APIからデータを取得
    legal_advice = get_legal_advice()
    
    if legal_advice:
        # 2. データをJSONファイルに保存
        filename = "legal_advice.json"
        save_to_json(legal_advice, filename)
        
        # 3. データを加工
        processed_data = process_legal_advice(filename)
        
        # 4. データを分析
        analyze_legal_advice(processed_data)
【python】

## 提出課題

以上の演習を通じて学んだことを活かして、以下の課題に取り組んでください：

1. 契約書テキストから特定の情報（当事者名、契約期間、金額など）を抽出するPythonスクリプトを作成してください
2. 複数の契約書ファイルを一括で処理し、抽出した情報をCSVファイルにまとめるスクリプトを作成してください
3. 上記の課題に取り組む中で工夫した点や苦労した点をレポートにまとめてください（400字程度）

提出方法：研修用ポータルサイトの課題提出ページからPythonスクリプトとレポートをアップロードしてください。
