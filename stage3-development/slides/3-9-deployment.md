# アプリケーションのデプロイと運用

## クラウドデプロイメントの基本

- インフラストラクチャの選択（IaaS, PaaS, SaaS）
- リージョンとアベイラビリティゾーンの選択
- スケーラビリティとパフォーマンスの考慮
- セキュリティとコンプライアンスの確保
- コスト最適化

## 主要なクラウドプラットフォーム

### AWS（Amazon Web Services）
- EC2（仮想マシン）
- ECS/EKS（コンテナオーケストレーション）
- Lambda（サーバーレス）
- RDS（データベース）
- S3（ストレージ）

### Microsoft Azure
- Virtual Machines
- Azure Kubernetes Service (AKS)
- Azure Functions
- Azure SQL Database
- Blob Storage

### Google Cloud Platform
- Compute Engine
- Google Kubernetes Engine (GKE)
- Cloud Functions
- Cloud SQL
- Cloud Storage

## デプロイメント戦略

### ブルー/グリーンデプロイメント
- 新旧バージョンを並行運用
- 切り替えはトラフィックルーティングで瞬時に実施
- ロールバックが容易
- リソース要件が2倍

【bash】
# AWS CLIを使用したブルー/グリーンデプロイメントの例
# 新しいターゲットグループの作成
aws elbv2 create-target-group \
  --name my-app-green \
  --protocol HTTP \
  --port 80 \
  --vpc-id vpc-12345678

# 新しいECSタスク定義のデプロイ
aws ecs update-service \
  --cluster my-cluster \
  --service my-service \
  --task-definition my-app:2 \
  --deployment-configuration maximumPercent=200,minimumHealthyPercent=100

# ロードバランサーのリスナールールを更新して新しいターゲットグループに切り替え
aws elbv2 modify-listener \
  --listener-arn arn:aws:elasticloadbalancing:region:account-id:listener/app/my-load-balancer/1234567890123456/1234567890123456 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:region:account-id:targetgroup/my-app-green/1234567890123456
【bash】

### カナリアデプロイメント
- トラフィックを段階的に新バージョンに移行
- リスクを最小限に抑えながら実環境でテスト可能
- 問題発生時の影響範囲を限定
- 実装が複雑

【yaml】
# Kubernetes Manifestを使用したカナリアデプロイメントの例
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: my-app
spec:
  hosts:
  - my-app.example.com
  http:
  - route:
    - destination:
        host: my-app-v1
        subset: v1
      weight: 80
    - destination:
        host: my-app-v2
        subset: v2
      weight: 20
【yaml】

## CI/CDパイプラインの構築

### CI/CDの基本概念
- 継続的インテグレーション（CI）：コードの変更を頻繁に統合
- 継続的デリバリー（CD）：本番環境へのデプロイを自動化
- 継続的デプロイメント：人間の介入なしで本番環境に自動デプロイ

### GitHub Actionsを使用したCI/CDパイプライン

【yaml】
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Test with pytest
      run: |
        pytest

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build and push Docker image
      uses: docker/build-push-action@v2
      with:
        context: .
        push: true
        tags: myregistry.io/my-app:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to production
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          docker pull myregistry.io/my-app:${{ github.sha }}
          docker-compose -f docker-compose.prod.yml up -d
【yaml】

## モニタリングとロギング

### モニタリングの基本
- インフラストラクチャモニタリング（CPU, メモリ, ディスク）
- アプリケーションパフォーマンスモニタリング（レスポンスタイム, エラー率）
- ユーザーエクスペリエンスモニタリング（ページロード時間, ユーザーフロー）

### Prometheusによるメトリクス収集

【yaml】
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'api'
    static_configs:
      - targets: ['api:8000']
  
  - job_name: 'web'
    static_configs:
      - targets: ['web:8501']
  
  - job_name: 'database'
    static_configs:
      - targets: ['db-exporter:9187']
【yaml】

### Grafanaによるダッシュボード

【bash】
# Grafanaのデプロイ
docker run -d -p 3000:3000 --name grafana \
  -e "GF_SECURITY_ADMIN_PASSWORD=secret" \
  --network monitoring-network \
  grafana/grafana
【bash】

### 構造化ロギング

【python】
import logging
import json
import time
from datetime import datetime

class StructuredLogger:
    def __init__(self, service_name):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        self.logger.addHandler(handler)
    
    def log(self, level, message, **kwargs):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "level": level,
            "message": message,
            **kwargs
        }
        self.logger.log(
            getattr(logging, level),
            json.dumps(log_data)
        )
    
    def info(self, message, **kwargs):
        self.log("INFO", message, **kwargs)
    
    def error(self, message, **kwargs):
        self.log("ERROR", message, **kwargs)
    
    def warning(self, message, **kwargs):
        self.log("WARNING", message, **kwargs)

# 使用例
logger = StructuredLogger("api-service")
logger.info("ユーザーがログインしました", user_id="12345", ip_address="192.168.1.1")
【python】

## セキュリティ対策

### セキュリティのベストプラクティス
- 最小権限の原則
- 多層防御
- 暗号化（転送中および保存時）
- 認証と認可
- 定期的なセキュリティ監査

### HTTPS/TLSの設定

【bash】
# Let's Encryptを使用した証明書の取得
docker run -it --rm \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/lib/letsencrypt:/var/lib/letsencrypt \
  certbot/certbot certonly --standalone \
  -d example.com -d www.example.com
【bash】

### シークレット管理

【yaml】
# docker-compose.yml
version: '3'

services:
  web:
    image: my-app:latest
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - API_KEY=${API_KEY}
      - SECRET_KEY=${SECRET_KEY}
    env_file:
      - .env.production
【yaml】

## 運用管理の自動化

### 自動スケーリング

【yaml】
# Kubernetes HPA (Horizontal Pod Autoscaler)
apiVersion: autoscaling/v2beta2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
【yaml】

### バックアップと復元

【bash】
# データベースのバックアップ
pg_dump -h db -U postgres -d mydb > backup_$(date +%Y%m%d).sql

# バックアップの自動化（cron）
0 2 * * * pg_dump -h db -U postgres -d mydb | gzip > /backups/mydb_$(date +\%Y\%m\%d).sql.gz

# バックアップの復元
gunzip -c backup_20230101.sql.gz | psql -h db -U postgres -d mydb
【bash】

## 次回予告：総合演習

- これまでの学習内容の統合
- 実践的なプロジェクト開発
- チーム開発の進め方
- 成果発表の準備 