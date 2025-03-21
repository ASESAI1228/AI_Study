# Supabase セットアップ手順

このドキュメントでは、AI_Studyプロジェクトで使用するSupabaseのセットアップ方法について説明します。

## Supabaseプロジェクトの作成

1. [Supabase](https://supabase.com/)にアクセスし、アカウントを作成・ログインします。
2. 新しいプロジェクトを作成します。
3. プロジェクト作成後、プロジェクトのダッシュボードから以下の情報を取得します：
   - Project URL: `https://your-project.supabase.co`
   - API Keys > anon public: `your-anon-key`

## データベーステーブルの作成

Supabaseのダッシュボードから「SQL Editor」を開き、以下のSQLを実行してテーブルを作成します。

### prompt_exercise_submissions テーブル

```sql
-- プロンプト演習の提出データを保存するテーブル
CREATE TABLE public.prompt_exercise_submissions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  exercise_type TEXT NOT NULL,
  user_id TEXT NOT NULL,
  submission_date TIMESTAMP WITH TIME ZONE DEFAULT now(),
  content JSONB NOT NULL
);

-- RLSポリシーの設定（必要に応じて）
ALTER TABLE public.prompt_exercise_submissions ENABLE ROW LEVEL SECURITY;

-- 匿名ユーザーが提出できるようにするポリシー
CREATE POLICY "Anyone can insert prompt submissions" 
  ON public.prompt_exercise_submissions 
  FOR INSERT 
  TO anon, authenticated 
  WITH CHECK (true);

-- 自分の提出データのみ閲覧可能にするポリシー
CREATE POLICY "Users can view their own submissions" 
  ON public.prompt_exercise_submissions 
  FOR SELECT 
  TO anon, authenticated 
  USING (user_id = auth.uid());
```

### exercise_submissions テーブル

```sql
-- 一般的な演習の提出データを保存するテーブル
CREATE TABLE public.exercise_submissions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_id TEXT NOT NULL,
  exercise_id TEXT NOT NULL,
  answers JSONB NOT NULL,
  is_submitted BOOLEAN DEFAULT false,
  submitted_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- RLSポリシーの設定（必要に応じて）
ALTER TABLE public.exercise_submissions ENABLE ROW LEVEL SECURITY;

-- 匿名ユーザーが提出できるようにするポリシー
CREATE POLICY "Anyone can insert exercise submissions" 
  ON public.exercise_submissions 
  FOR INSERT 
  TO anon, authenticated 
  WITH CHECK (true);

-- 自分の提出データのみ閲覧可能にするポリシー
CREATE POLICY "Users can view their own submissions" 
  ON public.exercise_submissions 
  FOR SELECT 
  TO anon, authenticated 
  USING (user_id = auth.uid());
```

## クライアント側の設定

Supabaseの接続情報を設定するには、以下のいずれかの方法を使用します：

### 1. 開発環境：ハードコードでの設定

`/website/stage1/js/supabase-client.js`の以下の部分を実際の値に変更します：

```javascript
const SUPABASE_URL = 'https://your-project.supabase.co';
const SUPABASE_KEY = 'your-anon-key';
```

### 2. 本番環境：環境変数を使用

#### 2.1 .env ファイルの作成

プロジェクトのルートディレクトリに`.env`ファイルを作成し、以下の内容を追加します：

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

#### 2.2 環境変数の読み込み

サーバーサイドで環境変数を読み込み、クライアントに提供する方法を実装します。例えば、Node.jsを使用している場合：

```javascript
// server.js
require('dotenv').config();
const express = require('express');
const app = express();

app.get('/api/config', (req, res) => {
  res.json({
    SUPABASE_URL: process.env.SUPABASE_URL,
    SUPABASE_ANON_KEY: process.env.SUPABASE_ANON_KEY
  });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

クライアント側では、この設定を取得して使用します：

```javascript
// クライアント側のコード
async function getConfig() {
  const response = await fetch('/api/config');
  const config = await response.json();
  return config;
}

// 設定を取得してSupabaseクライアントを初期化
getConfig().then(config => {
  const { SUPABASE_URL, SUPABASE_ANON_KEY } = config;
  const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  // ...
});
```

## セキュリティに関する注意事項

1. **アノニマスキーの扱い**: アノニマスキーはクライアントサイドで使用しても問題ありませんが、サービスキー（service_role key）は絶対に公開しないでください。

2. **Row Level Security (RLS)**: 適切なRLSポリシーを設定して、ユーザーが他のユーザーのデータにアクセスできないようにしてください。

3. **環境変数**: 本番環境では環境変数を使用し、ソースコードにキーを直接埋め込まないようにしてください。

4. **CORS設定**: Supabaseプロジェクトの設定で、適切なCORSポリシーを設定してください。

## トラブルシューティング

### 接続エラー

Supabaseへの接続に問題がある場合：

1. プロジェクトURLとアノニマスキーが正しいか確認してください。
2. ブラウザのコンソールでエラーメッセージを確認してください。
3. Supabaseダッシュボードで、プロジェクトのステータスが「Active」になっているか確認してください。

### データ保存エラー

データの保存に問題がある場合：

1. テーブル構造が正しいか確認してください。
2. RLSポリシーが適切に設定されているか確認してください。
3. 送信しているデータの形式が正しいか確認してください。

## 現在の実装について

現在の実装では、Supabase接続情報が設定されていない場合や接続に失敗した場合、自動的にローカルストレージを使用するフォールバック機能が実装されています。これにより、開発環境でもSupabaseを設定せずに基本的な機能をテストすることができます。
