# プロジェクト構造の定義と整理 (2025-03-16 16:07:41)

_**User**_

この構造でプロジェクトの形を作って
├── README.md                 # リポジトリの概要
├── CONTRIBUTING.md           # 貢献ガイドライン
├── LICENSE                   # ライセンス情報
├── docs/                     # 全体的なドキュメント
│   ├── curriculum.md         # カリキュラム全体像
│   ├── setup-guide.md        # 環境セットアップガイド
│   └── resources.md          # 参考資料リンク集
├── stage1-basics/            # 第1段階: 初心者向けAI基礎研修
│   ├── README.md             # 第1段階の概要
│   ├── slides/               # 講義スライド
│   │   ├── 1-1-introduction.md
│   │   ├── 1-2-ai-concepts.md
│   │   ├── 1-3-llm-overview.md
│   │   ├── 1-4-ai-services.md
│   │   ├── 1-5-prompt-engineering.md
│   │   ├── 1-6-legal-ai-applications.md
│   │   └── 1-7-ai-ethics.md
│   ├── exercises/            # 演習資料
│   │   ├── chatgpt-basics.md
│   │   └── prompt-practice.md
│   └── resources/            # 補足資料
│       └── ai-glossary.md
├── stage2-practical/         # 第2段階: LLMの基礎と実践研修
│   ├── README.md             # 第2段階の概要
│   ├── slides/               # 講義スライド
│   │   ├── 2-1-llm-mechanism.md
│   │   ├── 2-2-llm-strengths-weaknesses.md
│   │   ├── 2-3-advanced-llm-usage.md
│   │   ├── 2-4-efficiency-tips.md
│   │   └── 2-5-ai-checklist.md
│   ├── exercises/            # 演習資料
│   │   ├── contract-review.md
│   │   ├── sample-contracts/ # サンプル契約書
│   │   └── legal-research.md
│   └── resources/            # 補足資料
│       └── prompt-examples.md
├── stage3-development/       # 第3段階: API活用とローカル環境での実践研修
│   ├── README.md             # 第3段階の概要
│   ├── slides/               # 講義スライド
│   │   ├── 3-1-api-basics.md
│   │   ├── 3-2-openai-api.md
│   │   ├── 3-3-gemini-api.md
│   │   ├── 3-4-python-intro.md
│   │   ├── 3-5-database-supabase.md
│   │   └── 3-6-app-design.md
│   ├── exercises/            # 演習資料
│   │   ├── colab-notebooks/  # Google Colabノートブック
│   │   │   ├── api-intro.ipynb
│   │   │   └── supabase-intro.ipynb
│   │   └── miniprojects/     # ミニプロジェクト
│   │       ├── document-summarizer/
│   │       └── case-search/
│   ├── code/                 # サンプルコード
│   │   ├── api-examples/     # API呼び出しサンプル
│   │   │   ├── openai-example.py
│   │   │   └── supabase-example.py
│   │   ├── document-summarizer/  # 文書要約アプリ
│   │   │   ├── app.py
│   │   │   ├── templates/
│   │   │   └── requirements.txt
│   │   └── case-search/      # 判例検索アプリ
│   │       ├── app.py
│   │       ├── templates/
│   │       └── requirements.txt
│   └── resources/            # 補足資料
│       └── python-cheatsheet.md
└── stage4-advanced/          # 第4段階: 高度なAI活用とアプリデプロイ研修
    ├── README.md             # 第4段階の概要
    ├── slides/               # 講義スライド
    │   ├── 4-1-ai-coding-tools.md
    │   ├── 4-2-docker-intro.md
    │   ├── 4-3-docker-setup.md
    │   ├── 4-4-rag-concepts.md
    │   ├── 4-5-fine-tuning.md
    │   ├── 4-6-deployment.md
    │   └── 4-7-operations.md
    ├── exercises/            # 演習資料
    │   ├── docker-exercise.md
    │   ├── rag-implementation.md
    │   └── fine-tuning-demo.md
    ├── code/                 # サンプルコード
    │   ├── docker/           # Docker設定ファイル
    │   │   ├── Dockerfile
    │   │   └── docker-compose.yml
    │   ├── rag-system/       # RAG実装サンプル
    │   │   ├── app.py
    │   │   ├── embedding.py
    │   │   └── requirements.txt
    │   └── deployment/       # デプロイ関連
    │       ├── aws-setup.md
    │       └── local-setup.md
    └── project-template/     # 最終プロジェクトテンプレート
        ├── README.md
        ├── presentation-template.md
        └── evaluation-criteria.md

---
