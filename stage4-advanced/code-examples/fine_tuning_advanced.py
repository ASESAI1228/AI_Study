# 高度なファインチューニング実装例

import os
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
import openai
import time
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

# 環境変数の読み込み
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# ファインチューニング用データの準備
def prepare_training_data(data_path, output_path=None):
    """
    CSVまたはExcelファイルからファインチューニング用のJSONLデータを作成する
    
    Parameters:
    data_path (str): 入力データファイルのパス
    output_path (str, optional): 出力JSONLファイルのパス
    
    Returns:
    list: ファインチューニング用のデータリスト
    """
    # ファイル形式に応じてデータを読み込む
    if data_path.endswith('.csv'):
        df = pd.read_csv(data_path)
    elif data_path.endswith('.xlsx') or data_path.endswith('.xls'):
        df = pd.read_excel(data_path)
    else:
        raise ValueError("サポートされていないファイル形式です。CSVまたはExcelファイルを使用してください。")
    
    # データの検証
    required_columns = ['system_message', 'user_message', 'assistant_message']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"必要なカラム '{col}' がデータに含まれていません。")
    
    # ファインチューニング用のデータ形式に変換
    training_data = []
    for _, row in df.iterrows():
        # 各メッセージが空でないことを確認
        if pd.isna(row['system_message']) or pd.isna(row['user_message']) or pd.isna(row['assistant_message']):
            continue
            
        data_point = {
            "messages": [
                {"role": "system", "content": row['system_message']},
                {"role": "user", "content": row['user_message']},
                {"role": "assistant", "content": row['assistant_message']}
            ]
        }
        training_data.append(data_point)
    
    # JSONLファイルに保存（指定された場合）
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in training_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"{len(training_data)}件のトレーニングデータを{output_path}に保存しました。")
    
    return training_data

# データの分割（訓練用と検証用）
def split_data(data, test_size=0.2, random_state=42):
    """
    データを訓練用と検証用に分割する
    
    Parameters:
    data (list): 分割するデータリスト
    test_size (float): テストデータの割合
    random_state (int): 乱数シード
    
    Returns:
    tuple: (訓練データ, 検証データ)
    """
    train_data, valid_data = train_test_split(data, test_size=test_size, random_state=random_state)
    return train_data, valid_data

# ファインチューニングジョブの作成
def create_fine_tuning_job(training_file_id, validation_file_id=None, model="gpt-3.5-turbo", suffix=None):
    """
    ファインチューニングジョブを作成する
    
    Parameters:
    training_file_id (str): 訓練ファイルのID
    validation_file_id (str, optional): 検証ファイルのID
    model (str): ベースモデル名
    suffix (str, optional): モデル名の接尾辞
    
    Returns:
    dict: ファインチューニングジョブの情報
    """
    try:
        job_params = {
            "training_file": training_file_id,
            "model": model
        }
        
        if validation_file_id:
            job_params["validation_file"] = validation_file_id
            
        if suffix:
            job_params["suffix"] = suffix
        
        response = openai.FineTuningJob.create(**job_params)
        return response
    except Exception as e:
        print(f"ファインチューニングジョブの作成中にエラーが発生しました: {e}")
        return None

# ファインチューニングジョブのステータス確認
def check_fine_tuning_status(job_id):
    """
    ファインチューニングジョブのステータスを確認する
    
    Parameters:
    job_id (str): ジョブID
    
    Returns:
    dict: ジョブの情報
    """
    try:
        response = openai.FineTuningJob.retrieve(job_id)
        return response
    except Exception as e:
        print(f"ジョブステータスの確認中にエラーが発生しました: {e}")
        return None

# ファインチューニングジョブの完了を待機
def wait_for_fine_tuning_completion(job_id, check_interval=60):
    """
    ファインチューニングジョブの完了を待機する
    
    Parameters:
    job_id (str): ジョブID
    check_interval (int): ステータス確認の間隔（秒）
    
    Returns:
    dict: 完了したジョブの情報
    """
    print(f"ファインチューニングジョブ {job_id} の完了を待機中...")
    
    while True:
        job_info = check_fine_tuning_status(job_id)
        
        if not job_info:
            print("ジョブ情報の取得に失敗しました。再試行します...")
            time.sleep(check_interval)
            continue
        
        status = job_info.get("status")
        print(f"現在のステータス: {status}")
        
        if status == "succeeded":
            print("ファインチューニングが完了しました！")
            return job_info
        elif status in ["failed", "cancelled"]:
            print(f"ファインチューニングが失敗または中止されました: {status}")
            return job_info
        
        # 進捗状況の表示
        if "trained_tokens" in job_info and "training_file_tokens" in job_info:
            progress = (job_info["trained_tokens"] / job_info["training_file_tokens"]) * 100
            print(f"進捗: {progress:.2f}% ({job_info['trained_tokens']}/{job_info['training_file_tokens']} トークン)")
        
        time.sleep(check_interval)

# ファインチューニング済みモデルの評価
def evaluate_fine_tuned_model(model_id, test_data, temperature=0.0, max_tokens=500):
    """
    ファインチューニング済みモデルを評価する
    
    Parameters:
    model_id (str): モデルID
    test_data (list): テストデータ
    temperature (float): 生成の温度パラメータ
    max_tokens (int): 生成する最大トークン数
    
    Returns:
    pd.DataFrame: 評価結果のデータフレーム
    """
    results = []
    
    for i, item in enumerate(tqdm(test_data, desc="モデル評価中")):
        system_msg = next((msg["content"] for msg in item["messages"] if msg["role"] == "system"), "")
        user_msg = next((msg["content"] for msg in item["messages"] if msg["role"] == "user"), "")
        expected_answer = next((msg["content"] for msg in item["messages"] if msg["role"] == "assistant"), "")
        
        try:
            response = openai.ChatCompletion.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generated_answer = response.choices[0].message.content
            
            # 簡易的な評価指標（実際のプロジェクトではより高度な評価方法を使用）
            # 文字列の一致率（簡易的な方法）
            similarity = len(set(generated_answer.split()) & set(expected_answer.split())) / len(set(expected_answer.split()))
            
            results.append({
                "id": i,
                "user_message": user_msg,
                "expected_answer": expected_answer,
                "generated_answer": generated_answer,
                "similarity_score": similarity
            })
            
        except Exception as e:
            print(f"サンプル {i} の評価中にエラーが発生しました: {e}")
    
    return pd.DataFrame(results)

# 評価結果の可視化
def visualize_evaluation_results(eval_df):
    """
    評価結果を可視化する
    
    Parameters:
    eval_df (pd.DataFrame): 評価結果のデータフレーム
    """
    plt.figure(figsize=(10, 6))
    sns.histplot(eval_df['similarity_score'], bins=20, kde=True)
    plt.title('類似度スコアの分布')
    plt.xlabel('類似度スコア')
    plt.ylabel('頻度')
    plt.axvline(eval_df['similarity_score'].mean(), color='r', linestyle='--', label=f'平均: {eval_df["similarity_score"].mean():.2f}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('similarity_distribution.png')
    plt.close()
    
    # 最も類似度の低いサンプルと高いサンプルを表示
    print("\n最も類似度の低いサンプル:")
    worst_sample = eval_df.loc[eval_df['similarity_score'].idxmin()]
    print(f"ユーザーメッセージ: {worst_sample['user_message']}")
    print(f"期待される回答: {worst_sample['expected_answer']}")
    print(f"生成された回答: {worst_sample['generated_answer']}")
    print(f"類似度スコア: {worst_sample['similarity_score']:.2f}")
    
    print("\n最も類似度の高いサンプル:")
    best_sample = eval_df.loc[eval_df['similarity_score'].idxmax()]
    print(f"ユーザーメッセージ: {best_sample['user_message']}")
    print(f"期待される回答: {best_sample['expected_answer']}")
    print(f"生成された回答: {best_sample['generated_answer']}")
    print(f"類似度スコア: {best_sample['similarity_score']:.2f}")

# ファインチューニング済みモデルの使用例
def use_fine_tuned_model(model_id, system_message, user_message, temperature=0.7, max_tokens=500):
    """
    ファインチューニング済みモデルを使用する
    
    Parameters:
    model_id (str): モデルID
    system_message (str): システムメッセージ
    user_message (str): ユーザーメッセージ
    temperature (float): 生成の温度パラメータ
    max_tokens (int): 生成する最大トークン数
    
    Returns:
    str: 生成されたテキスト
    """
    try:
        response = openai.ChatCompletion.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"モデル使用中にエラーが発生しました: {e}")
        return None

# メイン処理
if __name__ == "__main__":
    # サンプルデータ（実際の使用時は自分のデータに置き換えてください）
    sample_data = [
        {
            "messages": [
                {"role": "system", "content": "あなたは法務アシスタントです。契約書の分析と法的アドバイスを提供します。"},
                {"role": "user", "content": "この秘密保持契約書の主な問題点を教えてください。"},
                {"role": "assistant", "content": "秘密保持契約書を拝見しないと具体的な問題点を指摘できませんが、一般的に確認すべき重要なポイントをご案内します：\n\n1. 秘密情報の定義が明確か\n2. 秘密保持義務の期間は適切か\n3. 例外規定（公知情報など）は含まれているか\n4. 情報の返却・破棄に関する条項はあるか\n5. 違反時の救済措置は明記されているか\n\n具体的な契約書をご提供いただければ、詳細な分析が可能です。"}
            ]
        },
        # 他のサンプルデータ...
    ]
    
    # 実際のファインチューニングプロセスはコメントアウト（APIキーと課金が必要なため）
    """
    # データの準備
    train_data, valid_data = split_data(sample_data)
    
    # JSONLファイルに保存
    train_file_path = "legal_train.jsonl"
    valid_file_path = "legal_valid.jsonl"
    
    with open(train_file_path, 'w', encoding='utf-8') as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
            
    with open(valid_file_path, 'w', encoding='utf-8') as f:
        for item in valid_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    # ファイルのアップロード
    train_file = openai.File.create(file=open(train_file_path, "rb"), purpose="fine-tune")
    valid_file = openai.File.create(file=open(valid_file_path, "rb"), purpose="fine-tune")
    
    # ファインチューニングジョブの作成
    job = create_fine_tuning_job(
        training_file_id=train_file.id,
        validation_file_id=valid_file.id,
        model="gpt-3.5-turbo",
        suffix="legal-assistant"
    )
    
    if job:
        # ジョブの完了を待機
        completed_job = wait_for_fine_tuning_completion(job.id)
        
        if completed_job and completed_job.get("status") == "succeeded":
            # モデルの評価
            model_id = completed_job.get("fine_tuned_model")
            eval_results = evaluate_fine_tuned_model(model_id, valid_data)
            
            # 評価結果の可視化
            visualize_evaluation_results(eval_results)
            
            # モデルの使用例
            system_msg = "あなたは法務アシスタントです。契約書の分析と法的アドバイスを提供します。"
            user_msg = "業務委託契約書における知的財産権の帰属条項について教えてください。"
            
            response = use_fine_tuned_model(model_id, system_msg, user_msg)
            print("\nファインチューニング済みモデルの回答:")
            print(response)
    """
    
    print("ファインチューニングの高度な実装例")
    print("実際にファインチューニングを実行するには、コメントアウトされたコードを有効にし、有効なAPIキーを設定してください。") 