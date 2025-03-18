# クラウドデプロイメントとCI/CD演習

## 目的

この演習では、法務AIアプリケーションをクラウド環境にデプロイし、継続的インテグレーション/継続的デリバリー（CI/CD）パイプラインを構築する方法を学びます。インフラストラクチャのコード化（IaC）、自動テスト、自動デプロイ、モニタリングの設定など、本番環境での運用に必要な技術を習得することを目的としています。

## 準備

1. 以下のアカウントを作成してください
   - AWS（Amazon Web Services）アカウント
   - GitHub アカウント
   - Docker Hub アカウント

2. 以下のツールをインストールしてください
   - AWS CLI
   - Terraform
   - Docker
   - kubectl（Kubernetes CLI）

3. 前回の演習で作成したDockerコンテナ化されたアプリケーションを用意してください
   - 用意できない場合は、`code-examples/docker_app`のサンプルを使用してください

## 演習1：インフラストラクチャのコード化（IaC）

### 課題1-1：Terraformの基本

1. 以下のコマンドを実行して、Terraformの動作を確認してください
   ```bash
   terraform --version
   ```

2. 以下の内容で`main.tf`ファイルを作成してください
   ```hcl
   provider "aws" {
     region = "ap-northeast-1"
   }
   
   resource "aws_s3_bucket" "terraform_state" {
     bucket = "your-name-legal-app-terraform-state"
     
     lifecycle {
       prevent_destroy = true
     }
   }
   
   resource "aws_s3_bucket_versioning" "terraform_state" {
     bucket = aws_s3_bucket.terraform_state.id
     versioning_configuration {
       status = "Enabled"
     }
   }
   ```

3. Terraformを初期化し、実行計画を確認してください
   ```bash
   terraform init
   terraform plan
   ```

### 課題1-2：AWSリソースのプロビジョニング

1. `code-examples/cicd/terraform`ディレクトリのファイルを参考に、以下のリソースを定義するTerraformコードを作成してください
   - VPC、サブネット、セキュリティグループ
   - RDSデータベース
   - ECSクラスター（またはEKSクラスター）
   - ロードバランサー

2. 変数を使用して環境ごとの設定を分離してください
   ```hcl
   variable "environment" {
     description = "デプロイ環境（development, staging, production）"
     type        = string
     default     = "development"
   }
   ```

3. 作成したTerraformコードを実行して、インフラストラクチャをプロビジョニングしてください
   ```bash
   terraform apply
   ```

## 演習2：CI/CDパイプラインの構築

### 課題2-1：GitHub Actionsの設定

1. アプリケーションのリポジトリに`.github/workflows`ディレクトリを作成してください

2. 以下の内容で`ci.yml`ファイルを作成してください
   ```yaml
   name: CI Pipeline
   
   on:
     push:
       branches: [ main, develop ]
     pull_request:
       branches: [ main, develop ]
   
   jobs:
     test:
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
           pip install pytest
       
       - name: Run tests
         run: pytest
   ```

3. GitHubリポジトリにコードをプッシュして、CIパイプラインが正常に動作することを確認してください

### 課題2-2：自動デプロイの設定

1. `code-examples/cicd/github-actions-workflow.yml`を参考に、以下の機能を持つCDパイプラインを設定してください
   - Dockerイメージのビルドとプッシュ
   - ステージング環境へのデプロイ（developブランチ）
   - 本番環境へのデプロイ（mainブランチ）

2. GitHubのSecretsに以下の情報を設定してください
   - `DOCKERHUB_USERNAME`
   - `DOCKERHUB_TOKEN`
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

3. CDパイプラインをテストするために、コードを変更してプッシュしてください

## 演習3：Kubernetesによるデプロイ

### 課題3-1：Kubernetesマニフェストの作成

1. 以下のリソースを定義するKubernetesマニフェストを作成してください
   - Deployment
   - Service
   - ConfigMap
   - Secret

2. 以下の内容で`deployment.yaml`ファイルを作成してください
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: legal-app
   spec:
     replicas: 2
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
           image: your-dockerhub-username/legal-app:latest
           ports:
           - containerPort: 8501
           env:
           - name: DB_HOST
             valueFrom:
               configMapKeyRef:
                 name: app-config
                 key: db_host
   ```

3. 環境ごとに異なる設定を持つマニフェストを作成してください（staging, production）

### 課題3-2：Kubernetesクラスターへのデプロイ

1. AWS EKSクラスターを作成するTerraformコードを作成してください

2. kubectlを使用してクラスターに接続してください
   ```bash
   aws eks update-kubeconfig --name legal-app-cluster --region ap-northeast-1
   ```

3. Kubernetesマニフェストを適用してアプリケーションをデプロイしてください
   ```bash
   kubectl apply -f k8s/staging/
   ```

4. デプロイしたアプリケーションにアクセスして動作を確認してください

## 演習4：モニタリングとロギングの設定

### 課題4-1：CloudWatchによるモニタリング

1. 以下のメトリクスを監視するCloudWatchダッシュボードを作成してください
   - CPU使用率
   - メモリ使用率
   - リクエスト数
   - レスポンスタイム

2. 異常を検知するためのCloudWatchアラームを設定してください
   - CPU使用率が80%を超えた場合
   - メモリ使用率が80%を超えた場合
   - エラーレートが5%を超えた場合

### 課題4-2：ログ管理

1. アプリケーションログをCloudWatchLogsに送信するように設定してください

2. ログを分析するためのCloudWatchLogsInsightsクエリを作成してください
   ```
   fields @timestamp, @message
   | filter @message like /ERROR/
   | sort @timestamp desc
   | limit 20
   ```

3. 重要なエラーが発生した場合にアラートを送信する仕組みを設定してください

## 演習5：セキュリティとコンプライアンスの確保

### 課題5-1：シークレット管理

1. AWS Secrets Managerを使用して以下のシークレットを管理してください
   - データベースのパスワード
   - APIキー

2. アプリケーションからSecrets Managerのシークレットを取得するコードを実装してください
   ```python
   import boto3
   
   def get_secret(secret_name):
       client = boto3.client('secretsmanager')
       response = client.get_secret_value(SecretId=secret_name)
       return response['SecretString']
   ```

### 課題5-2：セキュリティスキャンの導入

1. GitHubのDependabotを有効化して、依存関係の脆弱性をスキャンしてください

2. DockerイメージのセキュリティスキャンをCI/CDパイプラインに組み込んでください
   ```yaml
   - name: Scan Docker image
     uses: aquasecurity/trivy-action@master
     with:
       image-ref: 'your-dockerhub-username/legal-app:latest'
       format: 'table'
       exit-code: '1'
       ignore-unfixed: true
       severity: 'CRITICAL,HIGH'
   ```

## 提出課題

以上の演習を通じて学んだことを活かして、以下の課題に取り組んでください：

1. 法務AIアプリケーションの本番環境デプロイを実装してください
   - Terraformによるインフラストラクチャのコード化
   - GitHub ActionsによるCI/CDパイプライン
   - Kubernetesによるコンテナオーケストレーション
   - モニタリングとアラートの設定

2. 以下の要件を満たすようにしてください：
   - 高可用性（HA）設計
   - スケーラビリティの確保
   - セキュリティ対策の実装
   - コスト最適化

3. 以下の内容を含むレポートを作成してください（800〜1,200字程度）：
   - アーキテクチャの設計と実装方法
   - CI/CDパイプラインの構成
   - セキュリティ対策の詳細
   - 運用監視の方法
   - コスト最適化の取り組み

4. デプロイしたアプリケーションのデモンストレーション動画（3分程度）を作成してください

提出方法：研修用ポータルサイトの課題提出ページからTerraformコード、CI/CD設定ファイル、Kubernetesマニフェスト、レポート、デモ動画をアップロードしてください。 