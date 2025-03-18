# ファインチューニングのためのデータ準備サンプル

import json
import os
import pandas as pd
import re
from dotenv import load_dotenv
import openai

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# サンプルの法律質問と回答データ
legal_qa_data = [
    {
        "question": "秘密保持契約において、秘密情報の定義はどのように記載すべきですか？",
        "answer": "秘密保持契約における秘密情報の定義は、保護したい情報の範囲を明確にするために重要です。一般的には以下の要素を含めるべきです：\n\n1. 書面・口頭を問わず開示される全ての情報\n2. 「秘密」または「Confidential」等の表示がある情報\n3. 口頭で開示された場合は、一定期間内（通常14〜30日）に書面で確認された情報\n4. 秘密情報から除外される情報（公知の情報、受領者が独自に開発した情報など）\n\n具体的な記載例：「本契約において「秘密情報」とは、開示当事者が受領当事者に対して開示する一切の情報であって、有形の媒体に記録されている場合には秘密である旨の表示がなされているもの、または口頭で開示される場合には開示時に秘密である旨を明示し、かつ開示後14日以内に書面により内容を特定したものをいう。」"
    },
    {
        "question": "雇用契約書に必ず含めるべき条項は何ですか？",
        "answer": "雇用契約書に必ず含めるべき主要な条項は以下の通りです：\n\n1. 当事者の特定（雇用主と従業員の氏名・住所）\n2. 雇用期間（期間の定めの有無、開始日、終了日）\n3. 職務内容（役職、業務内容、勤務場所）\n4. 勤務時間・休日（始業・終業時間、休憩時間、休日、時間外労働）\n5. 賃金（基本給、手当、賞与、支払方法、支払日）\n6. 退職・解雇（退職手続き、解雇事由）\n7. 機密保持義務\n8. 競業避止義務（ある場合）\n\n特に労働基準法第15条および労働契約法第4条に基づき、労働条件（賃金、労働時間等）は書面で明示することが法的に求められています。"
    },
    {
        "question": "契約書における「不可抗力条項」の目的と一般的な記載内容を教えてください。",
        "answer": "不可抗力条項の目的は、当事者の合理的な制御を超えた事象により契約上の義務を履行できない場合に、債務不履行の責任を免除または軽減することです。\n\n一般的な記載内容：\n\n1. 不可抗力の定義：地震、台風、洪水などの自然災害、戦争、テロ、ストライキ、伝染病の流行、政府による規制など\n\n2. 通知義務：不可抗力事由の発生を知った当事者は、相手方に速やかに通知する義務\n\n3. 義務の免除または延期：不可抗力により影響を受けた義務の履行免除または延期の範囲\n\n4. 契約の終了：不可抗力が一定期間（例：連続30日間）継続した場合の契約解除権\n\n5. 費用負担：不可抗力期間中に発生した費用の負担方法\n\n記載例：「いずれの当事者も、地震、台風、洪水、火災、戦争、テロ行為、ストライキ、法令の制定・改廃、政府の命令・指示その他の当事者の合理的な支配を超えた事由（以下「不可抗力」という）により本契約上の義務の履行が遅延または妨げられた場合、その履行遅延または履行不能について責任を負わないものとする。」"
    },
    {
        "question": "業務委託契約における知的財産権の帰属はどのように定めるべきですか？",
        "answer": "業務委託契約における知的財産権の帰属条項は、成果物の権利関係を明確にするために重要です。一般的な考慮点と記載例は以下の通りです：\n\n【考慮点】\n1. 委託者（発注者）に全ての権利を帰属させる場合：最も一般的なパターンで、委託者が対価を支払って成果物を取得する場合に適しています。\n\n2. 受託者（請負者）に権利を残す場合：受託者が既存の技術やノウハウを活用する場合や、同様のサービスを他社にも提供する場合に適しています。この場合、委託者には利用権（ライセンス）を付与します。\n\n3. 共有とする場合：両者が共同で開発する場合や、両者の貢献が大きい場合に検討されます。\n\n【記載例（委託者帰属の場合）】\n「本業務の遂行により生じた成果物（プログラム、デザイン、文書等を含む）に関する著作権（著作権法第27条および第28条に規定する権利を含む）、特許権、実用新案権、意匠権、商標権その他一切の知的財産権（それらの登録を受ける権利を含む）は、委託者に帰属するものとする。受託者は委託者に対し、著作者人格権を行使しないものとする。」"
    },
    {
        "question": "契約書のレビュー時に特に注意すべきポイントを教えてください。",
        "answer": "契約書レビュー時の主要な注意ポイントは以下の通りです：\n\n1. 当事者の正確な特定：正式名称、住所、代表者名が正確か\n\n2. 契約の目的と範囲：何について合意しているのか明確か\n\n3. 権利義務の明確性：各当事者の権利と義務が具体的に記載されているか\n\n4. 重要な商業条件：価格、支払条件、納期、品質基準などが明確か\n\n5. 責任の範囲と制限：損害賠償の上限、免責事項が適切か\n\n6. 契約期間と終了条件：契約期間、更新方法、解除条件が明確か\n\n7. 秘密保持義務：秘密情報の定義と保護期間は適切か\n\n8. 知的財産権：権利の帰属、利用条件が明確か\n\n9. 紛争解決条項：準拠法、管轄裁判所または仲裁条項は適切か\n\n10. 不可抗力条項：免責される事由と手続きが明確か\n\n11. 契約の変更方法：書面による合意など変更手続きが定められているか\n\n12. 完全合意条項：本契約が当事者間の完全な合意を構成することが明記されているか\n\n13. 法的リスク：独占禁止法、下請法、個人情報保護法などの法令違反リスクはないか\n\n14. 自社にとって不利な条件：一方的な義務や過度なリスク負担がないか\n\nレビュー時は、契約の性質や業界特性に応じて重点的にチェックすべき項目を調整することが重要です。"
    }
]

# データをOpenAIのファインチューニング形式に変換する関数
def convert_to_openai_format(qa_data):
    formatted_data = []
    
    for item in qa_data:
        # システムメッセージを追加
        formatted_item = {
            "messages": [
                {"role": "system", "content": "あなたは法務アシスタントです。契約書や法律に関する質問に正確かつ簡潔に回答してください。"},
                {"role": "user", "content": item["question"]},
                {"role": "assistant", "content": item["answer"]}
            ]
        }
        formatted_data.append(formatted_item)
    
    return formatted_data

# データをJSONLファイルに保存する関数
def save_to_jsonl(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"データを{filename}に保存しました。")

# データを訓練用と検証用に分割する関数
def split_data(data, train_ratio=0.8):
    train_size = int(len(data) * train_ratio)
    train_data = data[:train_size]
    valid_data = data[train_size:]
    return train_data, valid_data

# データの品質をチェックする関数
def check_data_quality(data):
    issues = []
    
    for i, item in enumerate(data):
        messages = item["messages"]
        
        # システムメッセージのチェック
        if messages[0]["role"] != "system":
            issues.append(f"データ {i+1}: 最初のメッセージがシステムメッセージではありません")
        
        # ユーザーメッセージのチェック
        if messages[1]["role"] != "user":
            issues.append(f"データ {i+1}: 2番目のメッセージがユーザーメッセージではありません")
        
        # アシスタントメッセージのチェック
        if messages[2]["role"] != "assistant":
            issues.append(f"データ {i+1}: 3番目のメッセージがアシスタントメッセージではありません")
        
        # 内容の長さチェック
        if len(messages[1]["content"]) < 10:
            issues.append(f"データ {i+1}: ユーザーメッセージが短すぎます")
        
        if len(messages[2]["content"]) < 50:
            issues.append(f"データ {i+1}: アシスタントメッセージが短すぎます")
    
    return issues

# ファインチューニングのコスト見積もりを計算する関数
def estimate_cost(data, model="gpt-3.5-turbo", cost_per_1k_tokens=0.008):
    total_tokens = 0
    
    # 簡易的なトークン数の見積もり（実際のトークン数は異なる場合があります）
    for item in data:
        for message in item["messages"]:
            # 英語の場合、単語数の約1.3倍がトークン数の目安
            # 日本語の場合、文字数の約0.5倍がトークン数の目安
            content = message["content"]
            if re.search(r'[ぁ-んァ-ン一-龥]', content):  # 日本語が含まれているか
                token_estimate = len(content) * 0.5
            else:
                words = content.split()
                token_estimate = len(words) * 1.3
            
            total_tokens += token_estimate
    
    # コスト計算
    cost = (total_tokens / 1000) * cost_per_1k_tokens
    
    return {
        "estimated_tokens": int(total_tokens),
        "estimated_cost_usd": round(cost, 2)
    }

# ファインチューニングジョブを作成する関数
def create_fine_tuning_job(training_file_id, model="gpt-3.5-turbo"):
    try:
        response = openai.FineTuningJob.create(
            training_file=training_file_id,
            model=model
        )
        return response
    except Exception as e:
        print(f"ファインチューニングジョブの作成中にエラーが発生しました: {e}")
        return None

# ファインチューニング用のファイルをアップロードする関数
def upload_training_file(file_path):
    try:
        with open(file_path, "rb") as file:
            response = openai.File.create(
                file=file,
                purpose="fine-tune"
            )
        return response
    except Exception as e:
        print(f"ファイルのアップロード中にエラーが発生しました: {e}")
        return None

# メイン処理
if __name__ == "__main__":
    print("ファインチューニングデータ準備サンプルプログラム\n")
    
    # データをOpenAIのファインチューニング形式に変換
    formatted_data = convert_to_openai_format(legal_qa_data)
    
    # データの品質チェック
    issues = check_data_quality(formatted_data)
    if issues:
        print("データの品質問題:")
        for issue in issues:
            print(f"- {issue}")
    else:
        print("データの品質チェック: 問題なし")
    
    # コスト見積もり
    cost_estimate = estimate_cost(formatted_data)
    print(f"\n推定トークン数: {cost_estimate['estimated_tokens']}")
    print(f"推定コスト: ${cost_estimate['estimated_cost_usd']} USD")
    
    # データを訓練用と検証用に分割
    train_data, valid_data = split_data(formatted_data)
    print(f"\nデータを分割しました: 訓練用 {len(train_data)}件, 検証用 {len(valid_data)}件")
    
    # データをJSONLファイルに保存
    train_file = "legal_qa_train.jsonl"
    valid_file = "legal_qa_valid.jsonl"
    save_to_jsonl(train_data, train_file)
    save_to_jsonl(valid_data, valid_file)
    
    # 実際のファインチューニングプロセスはコメントアウト（APIキーと課金が必要なため）
    """
    # 訓練用ファイルをアップロード
    upload_response = upload_training_file(train_file)
    if upload_response:
        print(f"\nファイルをアップロードしました: {upload_response['id']}")
        
        # ファインチューニングジョブを作成
        job_response = create_fine_tuning_job(upload_response['id'])
        if job_response:
            print(f"ファインチューニングジョブを作成しました: {job_response['id']}")
            print(f"ステータス: {job_response['status']}")
    """
    
    print("\nファインチューニングの準備が完了しました。")
    print("実際のファインチューニングを実行するには、コメントアウトされたコードを有効にし、有効なAPIキーを設定してください。") 