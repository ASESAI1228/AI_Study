# クラウドデプロイメントとCI/CD

## クラウドデプロイメントの基礎

- クラウドコンピューティングの種類
  - IaaS（Infrastructure as a Service）
  - PaaS（Platform as a Service）
  - SaaS（Software as a Service）
  - FaaS（Function as a Service）

- 主要クラウドプロバイダー
  - AWS（Amazon Web Services）
  - Microsoft Azure
  - Google Cloud Platform（GCP）
  - Heroku, Render, Vercel, Netlify

## クラウドプラットフォームの選択基準

- コスト効率
- スケーラビリティ
- セキュリティ機能
- コンプライアンス対応
- 管理の容易さ
- サポートとドキュメント
- 既存システムとの統合性

## インフラストラクチャのコード化（IaC）

- Infrastructure as Code（IaC）の概念
- 主要なIaCツール
  - Terraform
  - AWS CloudFormation
  - Azure Resource Manager
  - Google Cloud Deployment Manager
  - Pulumi

## Terraformの基本

```hcl
# AWSプロバイダーの設定
provider "aws" {
  region = "ap-northeast-1"
}

# EC2インスタンスの定義
resource "aws_instance" "web_server" {
  ami           = "ami-0c3fd0f5d33134a76"
  instance_type = "t3.micro"
  
  tags = {
    Name = "legal-app-server"
    Environment = "production"
  }
}
```

## CI/CDの基本概念

- 継続的インテグレーション（CI）
  - コードの頻繁な統合
  - 自動テスト
  - 早期のバグ発見

- 継続的デリバリー/デプロイメント（CD）
  - 自動ビルド
  - 自動デプロイ
  - 環境間の一貫性

## CI/CDパイプラインの構成要素

1. ソースコード管理（Git）
2. ビルドプロセス
3. テスト自動化
4. アーティファクト管理
5. デプロイ自動化
6. モニタリングとフィードバック

## 主要なCI/CDツール

- GitHub Actions
- GitLab CI/CD
- Jenkins
- CircleCI
- Travis CI
- AWS CodePipeline
- Azure DevOps

## GitHub Actionsの基本

```yaml
name: Deploy Legal App

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: pytest
    
    - name: Build Docker image
      run: docker build -t legal-app:${{ github.sha }} .
    
    - name: Deploy to AWS
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ap-northeast-1
```

## 自動テストの実装

- 単体テスト（Unit Tests）
- 統合テスト（Integration Tests）
- エンドツーエンドテスト（E2E Tests）
- 負荷テスト（Load Tests）
- セキュリティテスト

```python
# Pytestを使用した単体テスト例
def test_extract_contract_info():
    sample_text = "契約期間: 2023年4月1日から2024年3月31日まで"
    result = extract_contract_info(sample_text)
    assert result["effective_date"] == "2023-04-01"
    assert result["expiration_date"] == "2024-03-31"
```

## デプロイ戦略

- ローリングデプロイ
- ブルー/グリーンデプロイ
- カナリアデプロイ
- フィーチャーフラグ

## コンテナオーケストレーション

- Kubernetes
- Amazon ECS/EKS
- Google Kubernetes Engine (GKE)
- Azure Kubernetes Service (AKS)

## Kubernetesの基本

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: legal-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: legal-app
  template:
    metadata:
      labels:
        app: legal-app
    spec:
      containers:
      - name: legal-app
        image: username/legal-app:latest
        ports:
        - containerPort: 8501
        env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: db_host
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: openai_api_key
```

## セキュリティのベストプラクティス

- シークレット管理
  - AWS Secrets Manager
  - HashiCorp Vault
  - GitHub Secrets
  - Kubernetes Secrets

- HTTPS/TLS対応
- IAM（Identity and Access Management）
- ネットワークセキュリティ
- コンテナセキュリティ
- コードスキャン

## モニタリングとロギング

- アプリケーションモニタリング
  - New Relic
  - Datadog
  - Prometheus + Grafana

- ログ管理
  - ELK Stack (Elasticsearch, Logstash, Kibana)
  - AWS CloudWatch
  - Google Cloud Logging

- アラート設定
- ダッシュボード作成

## スケーラビリティの確保

- 水平スケーリング vs 垂直スケーリング
- オートスケーリング
- ロードバランシング
- データベースのスケーリング
- キャッシュ戦略

## 障害復旧とバックアップ

- バックアップ戦略
- 障害復旧計画（DRP）
- 高可用性（HA）設計
- マルチリージョン展開
- RPO（Recovery Point Objective）とRTO（Recovery Time Objective）

## コスト最適化

- リソースの適切なサイジング
- スポットインスタンス/プリエンプティブVMの活用
- 自動スケーリングの設定
- リザーブドインスタンス/コミットメント割引
- 未使用リソースの特定と削除

## 次回予告：最終プロジェクト

- これまでの学習内容の統合
- 法務AIアプリケーションの設計と実装
- デプロイと運用
- プレゼンテーションとフィードバック 