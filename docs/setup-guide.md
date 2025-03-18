# 環境セットアップガイド

本研修プログラムを進めるにあたり、必要な環境のセットアップ方法を説明します。

## 必要なアカウント

以下のサービスのアカウントを事前に作成してください：

1. **OpenAI** - https://platform.openai.com/
   - APIキーを取得してください
   - 有料プランへの登録が必要です

2. **Google Cloud** - https://cloud.google.com/
   - Gemini APIを利用するためのAPIキーを取得してください
   - 無料枠で十分ですが、クレジットカード登録が必要です

3. **Supabase** - https://supabase.com/
   - 無料プランで十分です
   - プロジェクトを作成し、接続情報を取得してください

4. **GitHub** - https://github.com/
   - コードの管理とデプロイに使用します

## 必要なソフトウェア

### 基本ソフトウェア

- **Webブラウザ** - Google Chrome推奨
- **テキストエディタ** - Visual Studio Code推奨
- **Git** - バージョン管理システム

### 第3段階以降で必要なソフトウェア

- **Python** (バージョン3.8以上)
  - Windows: [公式サイト](https://www.python.org/downloads/)からインストーラをダウンロード
  - macOS: `brew install python3`
  - Linux: `sudo apt install python3 python3-pip`

- **Node.js** (バージョン16以上)
  - [公式サイト](https://nodejs.org/)からインストーラをダウンロード

- **Docker Desktop**
  - [公式サイト](https://www.docker.com/products/docker-desktop)からインストーラをダウンロード

## 環境変数の設定

第3段階以降では、以下の環境変数を設定する必要があります：

OPENAI_API_KEY=your_openai_api_key
GOOGLE_API_KEY=your_google_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key 