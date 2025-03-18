# Python基礎

## Pythonとは

- 読みやすく書きやすい高水準プログラミング言語
- 幅広い用途に使用される汎用言語
- AIや機械学習の分野で最も人気のある言語
- 豊富なライブラリとフレームワーク

## 開発環境のセットアップ

### インストール
- [Python公式サイト](https://www.python.org/)からダウンロード
- Windowsの場合：インストーラーを使用
- macOSの場合：Homebrewを使用 `brew install python`
- 仮想環境の作成：`python -m venv venv`

### 統合開発環境（IDE）
- Visual Studio Code + Python拡張機能
- PyCharm
- Jupyter Notebook（データ分析向け）

## 基本的な構文

### 変数と代入

【python】
# 変数の宣言と代入
name = "山田太郎"
age = 30
is_lawyer = True

# 複数の変数に同時に代入
x, y, z = 1, 2, 3
【python】

### データ型

【python】
# 整数型
count = 10

# 浮動小数点型
rate = 0.05

# 文字列型
message = "こんにちは"

# ブール型
is_valid = True

# リスト（配列）
names = ["田中", "鈴木", "佐藤"]

# 辞書（キーと値のペア）
person = {"name": "山田", "age": 30, "department": "法務部"}

# タプル（変更不可のリスト）
coordinates = (35.681236, 139.767125)
【python】

### 条件分岐

【python】
# if-elif-else文
age = 25
if age < 20:
    print("未成年です")
elif age < 65:
    print("成人です")
else:
    print("シニアです")

# 論理演算子
if age >= 20 and age < 65:
    print("就労年齢層です")

# 三項演算子
status = "成人" if age >= 20 else "未成年"
【python】

### ループ

【python】
# for文（リストの反復処理）
names = ["田中", "鈴木", "佐藤"]
for name in names:
    print(name)

# range関数を使ったループ
for i in range(5):  # 0から4まで
    print(i)

# while文
count = 0
while count < 5:
    print(count)
    count += 1
【python】

## 関数

### 関数の定義と呼び出し

【python】
# 基本的な関数
def greet(name):
    return f"こんにちは、{name}さん"

# 関数の呼び出し
message = greet("山田")
print(message)  # "こんにちは、山田さん"

# デフォルト引数
def greet_with_title(name, title="様"):
    return f"こんにちは、{name}{title}"

print(greet_with_title("山田"))  # "こんにちは、山田様"
print(greet_with_title("田中", "先生"))  # "こんにちは、田中先生"
【python】

### ラムダ関数（無名関数）

【python】
# ラムダ関数
double = lambda x: x * 2
print(double(5))  # 10

# リスト内の要素に対して関数を適用
numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))
print(doubled)  # [2, 4, 6, 8, 10]
【python】

## モジュールとパッケージ

### 標準ライブラリ

【python】
# 日付と時刻の操作
import datetime
today = datetime.date.today()
print(today)  # 2023-06-01

# ファイルシステム操作
import os
files = os.listdir(".")
print(files)  # カレントディレクトリのファイル一覧

# JSONデータの処理
import json
data = {"name": "山田", "age": 30}
json_str = json.dumps(data)
print(json_str)  # {"name": "山田", "age": 30}
【python】

### 外部パッケージのインストールと使用

【python】
# pipを使ったパッケージのインストール
pip install requests
【python】

【python】
# 外部パッケージの使用例（HTTP通信）
import requests
response = requests.get("https://api.example.com/data")
data = response.json()
【python】

## ファイル操作

### テキストファイルの読み書き

【python】
# ファイルの書き込み
with open("sample.txt", "w", encoding="utf-8") as f:
    f.write("これはサンプルテキストです。\n")
    f.write("2行目のテキストです。")

# ファイルの読み込み
with open("sample.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(content)

# 1行ずつ読み込み
with open("sample.txt", "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())  # strip()で改行を削除
【python】

## 例外処理

### try-except文

【python】
# 基本的な例外処理
try:
    number = int(input("数字を入力してください: "))
    result = 100 / number
    print(f"結果: {result}")
except ValueError:
    print("有効な数字を入力してください")
except ZeroDivisionError:
    print("0で割ることはできません")
except Exception as e:
    print(f"エラーが発生しました: {e}")
finally:
    print("処理を終了します")
【python】

## 次回予告：AI API入門

- OpenAI API概要
- Google AI (Gemini) API概要
- Anthropic Claude API概要
- API認証とセキュリティ 