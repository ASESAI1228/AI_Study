# APIリクエストの実装

## APIリクエストの基本構造

- エンドポイント：APIサーバーのURL
- HTTPメソッド：GET, POST, PUT, DELETE
- ヘッダー：認証情報や要求形式の指定
- リクエストボディ：送信するデータ
- クエリパラメータ：URLに付加する追加情報

## Pythonでのリクエスト実装

### requestsライブラリの基本

【python】
import requests

# GETリクエストの例
response = requests.get("https://api.example.com/data")

# POSTリクエストの例
data = {"prompt": "契約書を要約して", "max_tokens": 100}
headers = {"Authorization": f"Bearer {api_key}"}
response = requests.post(
    "https://api.example.com/generate",
    json=data,
    headers=headers
)

# レスポンスの処理
if response.status_code == 200:
    result = response.json()
    print(result)
else:
    print(f"エラー: {response.status_code}")
    print(response.text)
【python】

## エラーハンドリング

### 一般的なエラーコード
- 400: Bad Request（リクエスト形式の誤り）
- 401: Unauthorized（認証エラー）
- 403: Forbidden（権限エラー）
- 404: Not Found（リソースが存在しない）
- 429: Too Many Requests（レート制限超過）
- 500: Internal Server Error（サーバーエラー）

### エラー処理の実装

【python】
try:
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()  # エラーコードでは例外を発生
    result = response.json()
    return result
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        print("レート制限に達しました。しばらく待ってから再試行してください。")
    else:
        print(f"HTTPエラー: {e}")
except requests.exceptions.ConnectionError:
    print("接続エラー: APIサーバーに接続できません。")
except requests.exceptions.Timeout:
    print("タイムアウト: リクエストがタイムアウトしました。")
except requests.exceptions.RequestException as e:
    print(f"リクエストエラー: {e}")
except ValueError:
    print("JSONデコードエラー: レスポンスが有効なJSONではありません。")
【python】

## リトライ機能の実装

### 指数バックオフによるリトライ

【python】
import time
import random

def api_request_with_retry(url, data, headers, max_retries=5):
    retries = 0
    while retries < max_retries:
        try:
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
    
    return None  # 最大再試行回数に達した場合
【python】

## 非同期リクエストの実装

### asyncioとaiohttp

【python】
import asyncio
import aiohttp

async def fetch_data(session, url, data, headers):
    async with session.post(url, json=data, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"エラー: {response.status}")
            return None

async def process_multiple_requests(requests_data):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for req in requests_data:
            task = fetch_data(
                session, 
                req["url"], 
                req["data"], 
                req["headers"]
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

# 使用例
requests_data = [
    {"url": "https://api.example.com/endpoint", "data": {...}, "headers": {...}},
    {"url": "https://api.example.com/endpoint", "data": {...}, "headers": {...}},
    # ...
]

results = asyncio.run(process_multiple_requests(requests_data))
【python】

## セキュリティとベストプラクティス

### APIキーの安全な管理
- 環境変数の使用
- .envファイルと.gitignoreの設定
- シークレット管理サービスの活用

### リクエスト最適化
- 必要最小限のデータ送信
- バッチ処理の活用
- キャッシュの利用

### レート制限への対応
- リクエスト間隔の調整
- 429エラーの適切な処理
- 使用量のモニタリング

## 次回予告：データベース連携

- Supabaseの基本概念
- データベース設計の基礎
- PythonからのSQLクエリ実行
- 認証機能の実装 