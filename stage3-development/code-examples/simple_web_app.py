# Flaskを使用した簡易Webアプリケーション

from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import openai

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# Flaskアプリケーションの初期化
app = Flask(__name__)

# 契約書テンプレートのサンプルデータ
contract_templates = [
    {
        "id": 1,
        "name": "秘密保持契約書",
        "description": "情報の機密性を保護するための基本的な契約書",
        "variables": ["会社名1", "会社名2", "契約期間", "準拠法"]
    },
    {
        "id": 2,
        "name": "業務委託契約書",
        "description": "外部への業務委託のための契約書",
        "variables": ["委託者名", "受託者名", "業務内容", "委託料", "納期"]
    },
    {
        "id": 3,
        "name": "雇用契約書",
        "description": "従業員の雇用条件を定める契約書",
        "variables": ["会社名", "従業員名", "役職", "給与", "勤務地", "勤務時間"]
    }
]

# 契約書分析のサンプル関数
def analyze_contract(contract_text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは法務アシスタントです。契約書を分析し、重要なポイントと潜在的なリスクを特定してください。"},
                {"role": "user", "content": f"以下の契約書を分析してください:\n\n{contract_text}"}
            ],
            max_tokens=1000
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"分析中にエラーが発生しました: {str(e)}"

# 契約書生成のサンプル関数
def generate_contract(template_id, variables):
    # テンプレートIDに基づいて適切なプロンプトを作成
    template = next((t for t in contract_templates if t["id"] == template_id), None)
    
    if not template:
        return "テンプレートが見つかりません"
    
    # 変数の値を文字列に変換
    variables_str = "\n".join([f"{key}: {value}" for key, value in variables.items()])
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは法務アシスタントです。提供された情報に基づいて契約書を作成してください。"},
                {"role": "user", "content": f"{template['name']}を作成してください。以下の情報を使用してください:\n\n{variables_str}"}
            ],
            max_tokens=2000
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"生成中にエラーが発生しました: {str(e)}"

# ルートページ
@app.route('/')
def index():
    return render_template('index.html', templates=contract_templates)

# 契約書分析エンドポイント
@app.route('/analyze', methods=['POST'])
def analyze():
    contract_text = request.form.get('contract_text', '')
    
    if not contract_text:
        return jsonify({"error": "契約書のテキストが提供されていません"}), 400
    
    analysis = analyze_contract(contract_text)
    return jsonify({"analysis": analysis})

# 契約書生成エンドポイント
@app.route('/generate', methods=['POST'])
def generate():
    template_id = int(request.form.get('template_id', 0))
    variables = {}
    
    # フォームから変数を取得
    for key in request.form:
        if key.startswith('var_'):
            var_name = key[4:]  # 'var_' プレフィックスを削除
            variables[var_name] = request.form[key]
    
    if template_id == 0:
        return jsonify({"error": "テンプレートが選択されていません"}), 400
    
    contract = generate_contract(template_id, variables)
    return jsonify({"contract": contract})

# テンプレート詳細エンドポイント
@app.route('/template/<int:template_id>')
def template_details(template_id):
    template = next((t for t in contract_templates if t["id"] == template_id), None)
    
    if not template:
        return jsonify({"error": "テンプレートが見つかりません"}), 404
    
    return jsonify(template)

# メイン処理
if __name__ == '__main__':
    # templates ディレクトリが存在することを確認
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    # index.html が存在しない場合は作成
    if not os.path.exists('templates/index.html'):
        with open('templates/index.html', 'w') as f:
            f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>法務文書管理システム</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #333;
        }
        .tab {
            overflow: hidden;
            border: 1px solid #ccc;
            background-color: #f1f1f1;
            border-radius: 5px 5px 0 0;
        }
        .tab button {
            background-color: inherit;
            float: left;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 14px 16px;
            transition: 0.3s;
            font-size: 16px;
        }
        .tab button:hover {
            background-color: #ddd;
        }
        .tab button.active {
            background-color: #4CAF50;
            color: white;
        }
        .tabcontent {
            display: none;
            padding: 20px;
            border: 1px solid #ccc;
            border-top: none;
            border-radius: 0 0 5px 5px;
        }
        textarea {
            width: 100%;
            height: 200px;
            padding: 12px 20px;
            box-sizing: border-box;
            border: 2px solid #ccc;
            border-radius: 4px;
            background-color: #f8f8f8;
            resize: vertical;
            margin-bottom: 20px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 12px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .result {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 4px;
            background-color: #f9f9f9;
            white-space: pre-wrap;
        }
        .template-card {
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 15px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .template-card:hover {
            background-color: #f0f0f0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .form-group input {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>法務文書管理システム</h1>
        
        <div class="tab">
            <button class="tablinks active" onclick="openTab(event, 'analyze')">契約書分析</button>
            <button class="tablinks" onclick="openTab(event, 'generate')">契約書生成</button>
        </div>
        
        <div id="analyze" class="tabcontent" style="display: block;">
            <h2>契約書分析</h2>
            <p>分析したい契約書のテキストを入力してください。</p>
            <textarea id="contract-text" placeholder="ここに契約書のテキストを入力してください..."></textarea>
            <button onclick="analyzeContract()">分析する</button>
            <div id="analysis-result" class="result" style="display: none;"></div>
        </div>
        
        <div id="generate" class="tabcontent">
            <h2>契約書生成</h2>
            <p>テンプレートを選択して、必要な情報を入力してください。</p>
            
            <div id="template-selection">
                <h3>テンプレートを選択</h3>
                {% for template in templates %}
                <div class="template-card" onclick="selectTemplate({{ template.id }})">
                    <h4>{{ template.name }}</h4>
                    <p>{{ template.description }}</p>
                </div>
                {% endfor %}
            </div>
            
            <div id="template-form" style="display: none;">
                <h3 id="selected-template-name"></h3>
                <form id="contract-form">
                    <input type="hidden" id="template-id" name="template_id">
                    <div id="variable-fields"></div>
                    <button type="button" onclick="generateContract()">契約書を生成</button>
                </form>
            </div>
            
            <div id="generation-result" class="result" style="display: none;"></div>
        </div>
    </div>
    
    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
        
        function analyzeContract() {
            const contractText = document.getElementById('contract-text').value;
            if (!contractText) {
                alert('契約書のテキストを入力してください');
                return;
            }
            
            document.getElementById('analysis-result').innerHTML = '分析中...';
            document.getElementById('analysis-result').style.display = 'block';
            
            const formData = new FormData();
            formData.append('contract_text', contractText);
            
            fetch('/analyze', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('analysis-result').innerHTML = `エラー: ${data.error}`;
                } else {
                    document.getElementById('analysis-result').innerHTML = data.analysis;
                }
            })
            .catch(error => {
                document.getElementById('analysis-result').innerHTML = `エラー: ${error.message}`;
            });
        }
        
        function selectTemplate(templateId) {
            fetch(`/template/${templateId}`)
            .then(response => response.json())
            .then(template => {
                document.getElementById('template-selection').style.display = 'none';
                document.getElementById('template-form').style.display = 'block';
                document.getElementById('selected-template-name').textContent = template.name;
                document.getElementById('template-id').value = template.id;
                
                const variableFields = document.getElementById('variable-fields');
                variableFields.innerHTML = '';
                
                template.variables.forEach(variable => {
                    const formGroup = document.createElement('div');
                    formGroup.className = 'form-group';
                    
                    const label = document.createElement('label');
                    label.textContent = variable;
                    
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.name = `var_${variable}`;
                    input.placeholder = `${variable}を入力...`;
                    
                    formGroup.appendChild(label);
                    formGroup.appendChild(input);
                    variableFields.appendChild(formGroup);
                });
            })
            .catch(error => {
                alert(`テンプレート情報の取得に失敗しました: ${error.message}`);
            });
        }
        
        function generateContract() {
            const form = document.getElementById('contract-form');
            const formData = new FormData(form);
            
            document.getElementById('generation-result').innerHTML = '生成中...';
            document.getElementById('generation-result').style.display = 'block';
            
            fetch('/generate', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    document.getElementById('generation-result').innerHTML = `エラー: ${data.error}`;
                } else {
                    document.getElementById('generation-result').innerHTML = data.contract;
                }
            })
            .catch(error => {
                document.getElementById('generation-result').innerHTML = `エラー: ${error.message}`;
            });
        }
    </script>
</body>
</html>
            ''')
    
    # アプリケーションの実行
    app.run(debug=True) 