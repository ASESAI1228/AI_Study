# APIリクエスト実装サンプル

import requests
import time
import random
import os
import json
import asyncio
import aiohttp
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# APIキーの設定（環境変数から安全に読み込む）
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# 基本的なAPIリクエスト
def basic_api_request():
    print("=== 基本的なAPIリクエスト ===")
    
    # リクエスト先URL（例としてJSONPlaceholderの無料APIを使用）
    url = "https://jsonplaceholder.typicode.com/posts/1"
    
    # GETリクエストの実行
    response = requests.get(url)
    
    # レスポンスの処理
    if response.status_code == 200:
        data = response.json()
        print("リクエスト成功:")
        print(f"タイトル: {data['title']}")
        print(f"内容: {data['body']}")
    else:
        print(f"エラー: {response.status_code}")
        print(response.text)

# POSTリクエストの例
def post_request_example():
    print("\n=== POSTリクエストの例 ===")
    
    url = "https://jsonplaceholder.typicode.com/posts"
    
    # 送信するデータ
    data = {
        "title": "法的文書分析",
        "body": "契約書の自動分析と要約",
        "userId": 1
    }
    
    # POSTリクエストの実行
    response = requests.post(url, json=data)
    
    # レスポンスの処理
    if response.status_code == 201:  # 201はリソース作成成功
        result = response.json()
        print("投稿作成成功:")
        print(f"ID: {result['id']}")
        print(f"タイトル: {result['title']}")
    else:
        print(f"エラー: {response.status_code}")
        print(response.text)

# エラーハンドリングの例
def error_handling_example():
    print("\n=== エラーハンドリングの例 ===")
    
    # 存在しないURLにアクセス
    url = "https://jsonplaceholder.typicode.com/nonexistent"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # エラーコードでは例外を発生
        data = response.json()
        print("リクエスト成功:", data)
    except requests.exceptions.HTTPError as e:
        print(f"HTTPエラー: {e}")
    except requests.exceptions.ConnectionError:
        print("接続エラー: サーバーに接続できません。")
    except requests.exceptions.Timeout:
        print("タイムアウト: リクエストがタイムアウトしました。")
    except requests.exceptions.RequestException as e:
        print(f"リクエストエラー: {e}")
    except ValueError:
        print("JSONデコードエラー: レスポンスが有効なJSONではありません。")

# リトライ機能を持つAPIリクエスト
def api_request_with_retry(url, method="get", data=None, headers=None, max_retries=3):
    retries = 0
    while retries < max_retries:
        try:
            if method.lower() == "get":
                response = requests.get(url, headers=headers)
            else:  # post
                response = requests.post(url, json=data, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # レート制限エラーの場合、指数バックオフで待機
                wait_time = (2 ** retries) + random.random()
                print(f"レート制限に達しました。{wait_time:.2f}秒待機します...")
                time.sleep(wait_time)
                retries += 1
            else:
                # その他のHTTPエラーはすぐに再試行しない
                print(f"HTTPエラー: {e}")
                break
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # 接続エラーやタイムアウトは再試行
            wait_time = (2 ** retries) + random.random()
            print(f"接続エラー。{wait_time:.2f}秒後に再試行します...")
            time.sleep(wait_time)
            retries += 1
        except Exception as e:
            # その他のエラーは再試行しない
            print(f"エラー: {e}")
            break
    
    print(f"最大再試行回数（{max_retries}回）に達しました。")
    return None

# リトライ機能のデモ
def retry_demo():
    print("\n=== リトライ機能のデモ ===")
    
    # 意図的に存在しないURLを指定
    url = "https://jsonplaceholder.typicode.com/nonexistent"
    result = api_request_with_retry(url, max_retries=2)
    
    if result:
        print("リクエスト成功:", result)
    else:
        print("リクエストは失敗しました。")

# 非同期リクエストの実装
async def fetch_data(session, url, method="get", data=None, headers=None):
    try:
        if method.lower() == "get":
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"エラー: {response.status}")
                    return None
        else:  # post
            async with session.post(url, json=data, headers=headers) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    print(f"エラー: {response.status}")
                    return None
    except Exception as e:
        print(f"リクエストエラー: {e}")
        return None

async def process_multiple_requests(requests_data):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for req in requests_data:
            task = fetch_data(
                session, 
                req["url"], 
                req.get("method", "get"),
                req.get("data"),
                req.get("headers")
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

# 非同期リクエストのデモ
def async_requests_demo():
    print("\n=== 非同期リクエストのデモ ===")
    
    # 複数のリクエストを準備
    requests_data = [
        {"url": "https://jsonplaceholder.typicode.com/posts/1", "method": "get"},
        {"url": "https://jsonplaceholder.typicode.com/posts/2", "method": "get"},
        {"url": "https://jsonplaceholder.typicode.com/posts/3", "method": "get"},
        {"url": "https://jsonplaceholder.typicode.com/posts", "method": "post", 
         "data": {"title": "非同期リクエストのテスト", "body": "テスト本文", "userId": 1}}
    ]
    
    # 非同期リクエストの実行
    results = asyncio.run(process_multiple_requests(requests_data))
    
    # 結果の表示
    print("非同期リクエスト結果:")
    for i, result in enumerate(results):
        if result:
            if "title" in result:
                print(f"リクエスト {i+1}: {result['title']}")
            else:
                print(f"リクエスト {i+1}: {result}")
        else:
            print(f"リクエスト {i+1}: 失敗")

# OpenAI APIへのリクエスト例
def openai_api_request():
    print("\n=== OpenAI APIリクエスト例 ===")
    
    if not OPENAI_API_KEY:
        print("OpenAI APIキーが設定されていません。")
        return
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "あなたは法務アシスタントです。"},
            {"role": "user", "content": "契約書における不可抗力条項の重要性を簡潔に説明してください。"}
        ],
        "max_tokens": 150
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            print("OpenAI APIレスポンス:")
            print(content)
        else:
            print("有効なレスポンスが返されませんでした。")
    except Exception as e:
        print(f"OpenAI APIリクエストエラー: {e}")

# メイン処理
if __name__ == "__main__":
    # 基本的なAPIリクエスト
    basic_api_request()
    
    # POSTリクエストの例
    post_request_example()
    
    # エラーハンドリングの例
    error_handling_example()
    
    # リトライ機能のデモ
    retry_demo()
    
    # 非同期リクエストのデモ
    async_requests_demo()
    
    # OpenAI APIリクエスト例（APIキーが設定されている場合のみ実行）
    openai_api_request() 