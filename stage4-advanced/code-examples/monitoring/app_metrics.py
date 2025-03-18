# アプリケーションメトリクス収集用のコード

import time
from prometheus_client import Counter, Histogram, Gauge, Summary, start_http_server
import threading
import random
import psycopg2
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# メトリクスの定義
HTTP_REQUESTS_TOTAL = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'handler', 'status']
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'handler'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 5, 10]
)

ACTIVE_REQUESTS = Gauge(
    'active_requests',
    'Number of active HTTP requests'
)

DB_QUERY_DURATION_SECONDS = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 5, 10]
)

AI_API_REQUESTS_TOTAL = Counter(
    'ai_api_requests_total',
    'Total number of AI API requests',
    ['api_type', 'status']
)

AI_API_DURATION_SECONDS = Histogram(
    'ai_api_duration_seconds',
    'AI API request duration in seconds',
    ['api_type'],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30]
)

DOCUMENT_PROCESSING_DURATION_SECONDS = Histogram(
    'document_processing_duration_seconds',
    'Document processing duration in seconds',
    ['document_type'],
    buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60]
)

MEMORY_USAGE_BYTES = Gauge(
    'app_memory_usage_bytes',
    'Memory usage in bytes'
)

CPU_USAGE_PERCENT = Gauge(
    'app_cpu_usage_percent',
    'CPU usage in percent'
)

# HTTPリクエストのメトリクス収集用デコレータ
def track_request(handler_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            method = 'GET'  # 実際のアプリケーションでは動的に取得
            
            ACTIVE_REQUESTS.inc()
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                status = '200'  # 成功時
                return result
            except Exception as e:
                status = '500'  # エラー時
                raise e
            finally:
                duration = time.time() - start_time
                HTTP_REQUEST_DURATION_SECONDS.labels(
                    method=method,
                    handler=handler_name
                ).observe(duration)
                
                HTTP_REQUESTS_TOTAL.labels(
                    method=method,
                    handler=handler_name,
                    status=status
                ).inc()
                
                ACTIVE_REQUESTS.dec()
        
        return wrapper
    return decorator

# データベースクエリのメトリクス収集
def track_db_query(query_type):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                DB_QUERY_DURATION_SECONDS.labels(
                    query_type=query_type
                ).observe(duration)
        
        return wrapper
    return decorator

# AI APIリクエストのメトリクス収集
def track_ai_api_request(api_type):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                AI_API_REQUESTS_TOTAL.labels(
                    api_type=api_type,
                    status='success'
                ).inc()
                return result
            except Exception as e:
                AI_API_REQUESTS_TOTAL.labels(
                    api_type=api_type,
                    status='error'
                ).inc()
                raise e
            finally:
                duration = time.time() - start_time
                AI_API_DURATION_SECONDS.labels(
                    api_type=api_type
                ).observe(duration)
        
        return wrapper
    return decorator

# リソース使用状況の定期的な収集
def collect_resource_metrics():
    import psutil
    
    while True:
        # メモリ使用量
        memory_info = psutil.Process().memory_info()
        MEMORY_USAGE_BYTES.set(memory_info.rss)
        
        # CPU使用率
        CPU_USAGE_PERCENT.set(psutil.Process().cpu_percent(interval=1))
        
        time.sleep(15)  # 15秒ごとに収集

# メトリクスサーバーの起動
def start_metrics_server(port=8000):
    start_http_server(port)
    print(f"Metrics server started on port {port}")
    
    # リソースメトリクス収集スレッドの開始
    thread = threading.Thread(target=collect_resource_metrics, daemon=True)
    thread.start()

# 使用例
if __name__ == "__main__":
    # メトリクスサーバーの起動
    start_metrics_server()
    
    # サンプルのメトリクス生成（実際のアプリケーションでは実際の処理に組み込む）
    @track_request("sample_handler")
    def sample_request():
        time.sleep(random.uniform(0.05, 0.5))
        return {"status": "success"}
    
    @track_db_query("select")
    def sample_db_query():
        time.sleep(random.uniform(0.01, 0.2))
        return [{"id": 1, "name": "Sample"}]
    
    @track_ai_api_request("openai")
    def sample_ai_api_call():
        time.sleep(random.uniform(0.5, 2.0))
        return {"response": "AI generated content"}
    
    # サンプルリクエストの実行
    while True:
        sample_request()
        sample_db_query()
        sample_ai_api_call()
        time.sleep(1) 