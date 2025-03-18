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