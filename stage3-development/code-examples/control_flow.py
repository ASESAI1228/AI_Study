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