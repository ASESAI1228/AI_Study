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