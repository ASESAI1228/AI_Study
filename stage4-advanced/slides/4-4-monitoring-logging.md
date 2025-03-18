# モニタリングとロギング

## モニタリングとロギングの重要性

- システムの健全性と可用性の確保
- パフォーマンスボトルネックの特定
- セキュリティインシデントの検出
- ユーザー行動の理解
- ビジネスメトリクスの追跡
- コンプライアンス要件の充足

## モニタリングの基本概念

- メトリクス：数値データ（CPU使用率、メモリ使用量、リクエスト数など）
- アラート：閾値を超えた場合の通知
- ダッシュボード：メトリクスの可視化
- ヘルスチェック：システムコンポーネントの状態確認
- SLI（Service Level Indicator）：サービスレベルの指標
- SLO（Service Level Objective）：サービスレベルの目標

## Prometheusによるモニタリング

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'legal_app'
    static_configs:
      - targets: ['app:8000']
  
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

## Prometheusのアラートルール

```yaml
groups:
  - name: legal_app_alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 5 minutes on {{ $labels.instance }}"
```

## Grafanaによる可視化

- 複数データソースの統合（Prometheus、Elasticsearch、CloudWatchなど）
- インタラクティブなダッシュボード
- アラート通知の設定
- ユーザー権限管理
- アノテーション（イベントマーキング）

## ロギングの基本概念

- 構造化ロギング：JSONなどの形式でログを記録
- ログレベル：DEBUG、INFO、WARN、ERROR、FATAL
- 集中型ログ管理：複数サーバーからのログを一元管理
- ログローテーション：ログファイルの肥大化防止
- ログ保持ポリシー：ログの保存期間設定

## ELKスタック

- Elasticsearch：ログデータの保存と検索
- Logstash：ログデータの収集と変換
- Kibana：ログデータの可視化
- Beats：軽量データシッパー（Filebeat、Metricbeatなど）

## Fluentdによるログ収集

```
<source>
  @type forward
  port 24224
  bind 0.0.0.0
</source>

<match legal-app.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  logstash_format true
  logstash_prefix legal-app
  include_tag_key true
  tag_key @log_name
  flush_interval 5s
</match>
```

## アプリケーションログの構造化

```python
import logging
import json
import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'request_id'):
            log_record["request_id"] = record.request_id
            
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)
```

## 分散トレーシング

- マイクロサービス間のリクエストフロー追跡
- パフォーマンスボトルネックの特定
- エラー発生箇所の特定
- ツール：Jaeger、Zipkin、AWS X-Ray

## 異常検知

- 統計的手法：移動平均、標準偏差
- 機械学習手法：異常検知アルゴリズム
- ルールベース：閾値とパターンマッチング
- 時系列分析：季節性と傾向の分離

## モニタリングとロギングのベストプラクティス

- 必要なメトリクスとログの特定
- 適切な粒度の設定
- セキュリティとプライバシーの考慮
- リソース使用量の最適化
- アラート疲れの防止
- 自動化の活用

## 法務AIアプリケーションのモニタリング戦略

- システムメトリクス：CPU、メモリ、ディスク、ネットワーク
- アプリケーションメトリクス：レスポンスタイム、エラー率、同時接続数
- ビジネスメトリクス：契約書処理数、AI API呼び出し数、ユーザーアクション
- セキュリティメトリクス：認証試行、権限変更、機密データアクセス

## 次回予告：クラウドデプロイメントとCI/CD

- クラウドプラットフォームの選択
- インフラストラクチャのコード化（IaC）
- CI/CDパイプラインの構築
- 自動テストと品質保証
- スケーラビリティとパフォーマンス最適化 