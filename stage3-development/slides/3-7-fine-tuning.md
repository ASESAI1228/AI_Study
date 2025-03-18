# ファインチューニングの基礎

## ファインチューニングとは

- 事前学習済みの大規模言語モデル（LLM）を特定のタスクや領域に適応させる技術
- 少量の専門データを使用して、モデルの出力を調整
- 特定のスタイル、トーン、フォーマットに合わせた応答を生成
- 専門知識や組織固有の情報を反映した回答が可能

## ファインチューニングのメリット

- プロンプトエンジニアリングだけでは達成できない一貫性
- トークン使用量の削減（長いプロンプトが不要に）
- レイテンシの改善（短いプロンプトで高品質な応答）
- 特定ドメインでの精度向上
- 組織固有の知識やスタイルの反映

## ファインチューニングの適用シナリオ

- 特定のトーンやスタイルでの一貫した応答
- 特定フォーマットでのデータ出力
- 専門分野（法律、医療、金融など）での正確な応答
- 組織固有の知識ベースに基づく回答
- 特定のタスク（分類、要約、抽出など）の最適化

## データセットの準備

### データ形式

【python】
# OpenAIのファインチューニング用JSONLフォーマット
[
  {
    "messages": [
      {"role": "system", "content": "あなたは法務アシスタントです。契約書の分析と法的アドバイスを提供します。"},
      {"role": "user", "content": "この秘密保持契約書の主な問題点を教えてください。"},
      {"role": "assistant", "content": "秘密保持契約書を拝見しないと具体的な問題点を指摘できませんが、一般的に確認すべき重要なポイントをご案内します：\n\n1. 秘密情報の定義が明確か\n2. 秘密保持義務の期間は適切か\n3. 例外規定（公知情報など）は含まれているか\n4. 情報の返却・破棄に関する条項はあるか\n5. 違反時の救済措置は明記されているか\n\n具体的な契約書をご提供いただければ、詳細な分析が可能です。"}
    ]
  },
  {
    "messages": [
      {"role": "system", "content": "あなたは法務アシスタントです。契約書の分析と法的アドバイスを提供します。"},
      {"role": "user", "content": "雇用契約書に含めるべき重要な条項は何ですか？"},
      {"role": "assistant", "content": "雇用契約書に含めるべき重要な条項は以下の通りです：\n\n1. 基本情報（雇用開始日、役職、勤務地）\n2. 雇用形態（正社員、契約社員、パートタイム等）\n3. 報酬条件（給与、ボーナス、昇給制度）\n4. 勤務条件（勤務時間、休憩、休日、残業）\n5. 福利厚生（社会保険、有給休暇、その他手当）\n6. 機密保持義務\n7. 競業避止義務\n8. 知的財産権の帰属\n9. 懲戒・解雇条件\n10. 契約終了条件\n11. 紛争解決方法\n\n各条項は適用される労働法規に準拠し、明確かつ公正な内容である必要があります。"}
    ]
  }
]
【python】

### データ品質の確保

- 高品質な回答例の作成
- 多様なケースのカバー
- 一貫したフォーマットとスタイル
- バイアスの排除
- 適切なデータ量の確保（最低20-50例）

### データ前処理

【python】
import json
import pandas as pd
import random

# CSVからJSONLへの変換
def csv_to_jsonl(csv_file, jsonl_file, system_prompt):
    # CSVファイルの読み込み
    df = pd.read_csv(csv_file)
    
    # JSONLフォーマットに変換
    jsonl_data = []
    for _, row in df.iterrows():
        entry = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": row["question"]},
                {"role": "assistant", "content": row["answer"]}
            ]
        }
        jsonl_data.append(entry)
    
    # JSONLファイルに書き込み
    with open(jsonl_file, "w", encoding="utf-8") as f:
        for entry in jsonl_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# データの分割（訓練用と検証用）
def split_data(jsonl_file, train_file, val_file, val_ratio=0.2):
    # JSONLファイルの読み込み
    with open(jsonl_file, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]
    
    # データのシャッフル
    random.shuffle(data)
    
    # 訓練用と検証用に分割
    split_idx = int(len(data) * (1 - val_ratio))
    train_data = data[:split_idx]
    val_data = data[split_idx:]
    
    # ファイルに書き込み
    with open(train_file, "w", encoding="utf-8") as f:
        for entry in train_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    
    with open(val_file, "w", encoding="utf-8") as f:
        for entry in val_data:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
【python】

## OpenAI APIを使用したファインチューニング

### ファイルのアップロード

【python】
import openai
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# トレーニングファイルのアップロード
def upload_training_file(file_path):
    try:
        with open(file_path, "rb") as file:
            response = openai.files.create(
                file=file,
                purpose="fine-tune"
            )
        print(f"ファイルがアップロードされました。File ID: {response.id}")
        return response.id
    except Exception as e:
        print(f"ファイルのアップロードに失敗しました: {e}")
        return None
【python】

### ファインチューニングジョブの作成

【python】
# ファインチューニングジョブの作成
def create_fine_tuning_job(file_id, model="gpt-3.5-turbo", n_epochs=3):
    try:
        response = openai.fine_tuning.jobs.create(
            training_file=file_id,
            model=model,
            hyperparameters={
                "n_epochs": n_epochs
            }
        )
        print(f"ファインチューニングジョブが作成されました。Job ID: {response.id}")
        return response.id
    except Exception as e:
        print(f"ファインチューニングジョブの作成に失敗しました: {e}")
        return None
【python】

### ジョブのステータス確認

【python】
# ファインチューニングジョブのステータス確認
def get_fine_tuning_job_status(job_id):
    try:
        response = openai.fine_tuning.jobs.retrieve(job_id)
        print(f"ジョブID: {response.id}")
        print(f"ステータス: {response.status}")
        print(f"作成日時: {response.created_at}")
        print(f"完了日時: {response.finished_at}")
        print(f"モデル: {response.model}")
        print(f"ファインチューニング済みモデル: {response.fine_tuned_model}")
        return response
    except Exception as e:
        print(f"ジョブステータスの取得に失敗しました: {e}")
        return None
【python】

## ファインチューニング済みモデルの使用

【python】
# ファインチューニング済みモデルを使用した回答生成
def generate_response(fine_tuned_model, prompt, system_prompt=None):
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = openai.chat.completions.create(
            model=fine_tuned_model,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"回答生成に失敗しました: {e}")
        return None
【python】

## モデルの評価

### 評価指標

- 正確性（Accuracy）
- 一貫性（Consistency）
- 関連性（Relevance）
- 専門性（Expertise）
- 応答品質（Response Quality）

### 評価方法

【python】
import pandas as pd
import numpy as np

# モデル評価関数
def evaluate_model(model, test_data, system_prompt=None):
    results = []
    
    for item in test_data:
        question = item["messages"][1]["content"]  # ユーザーの質問
        expected_answer = item["messages"][2]["content"]  # 期待される回答
        
        # モデルからの回答を取得
        actual_answer = generate_response(model, question, system_prompt)
        
        # 評価者による手動評価（実際の実装では自動評価も検討）
        print(f"\n質問: {question}")
        print(f"\n期待される回答: {expected_answer}")
        print(f"\nモデルの回答: {actual_answer}")
        
        accuracy = float(input("正確性 (0-5): "))
        relevance = float(input("関連性 (0-5): "))
        expertise = float(input("専門性 (0-5): "))
        
        results.append({
            "question": question,
            "expected_answer": expected_answer,
            "actual_answer": actual_answer,
            "accuracy": accuracy,
            "relevance": relevance,
            "expertise": expertise,
            "average_score": np.mean([accuracy, relevance, expertise])
        })
    
    # 結果の集計
    df = pd.DataFrame(results)
    print("\n評価結果:")
    print(f"平均正確性: {df['accuracy'].mean():.2f}")
    print(f"平均関連性: {df['relevance'].mean():.2f}")
    print(f"平均専門性: {df['expertise'].mean():.2f}")
    print(f"総合スコア: {df['average_score'].mean():.2f}")
    
    return df
【python】

## ベストプラクティスとコスト最適化

### ベストプラクティス
- 高品質なトレーニングデータの準備
- 適切なエポック数の選択
- 定期的な評価と改善
- システムプロンプトとの組み合わせ

### コスト最適化
- 必要最小限のデータセットサイズ
- 適切なモデル選択（gpt-3.5-turbo vs gpt-4）
- バッチ処理の活用
- 定期的なモデル更新の計画

## 次回予告：Docker環境の構築と活用

- Dockerの基本概念
- コンテナ化のメリット
- Dockerfileの作成
- Docker Composeによる複数サービスの連携 