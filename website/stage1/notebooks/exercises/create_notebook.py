import nbformat as nbf
import os

# Create a new notebook
nb = nbf.v4.new_notebook()

# Create markdown and code cells for the notebook
cells = [
    nbf.v4.new_markdown_cell("# プロンプト作成演習 - 模範解答\n\nこのノートブックでは、プロンプト作成演習の模範解答と解説を提供します。"),
    
    # 演習1
    nbf.v4.new_markdown_cell("## 演習1：基本的なプロンプト設計"),
    nbf.v4.new_markdown_cell("### タスク1：契約書の重要条項の抽出と分析"),
    nbf.v4.new_code_cell('"""契約書分析プロンプト例\n[契約書全文をここに貼り付け]\n\n具体的に以下の項目について抽出・分析してください：\n1. 契約当事者と役割\n2. 契約期間と更新条件\n..."""'),
    
    # 演習2
    nbf.v4.new_markdown_cell("## 演習2：プロンプトパターンの適用"),
    nbf.v4.new_markdown_cell("### パターン1：ロールプロンプト"),
    nbf.v4.new_code_cell('"""あなたは大手法律事務所の契約審査部門で10年以上の経験を持つ弁護士です。..."""'),
    
    # 演習3
    nbf.v4.new_markdown_cell("## 演習3：プロンプトの反復的改善"),
    nbf.v4.new_markdown_cell("### 初期プロンプトから改善プロンプトへ"),
    nbf.v4.new_code_cell('"""初期: この法律文書を要約してください。\n\n改善: あなたは法律文書を一般の人にも理解しやすく説明する専門家です。..."""'),
    
    # 演習4
    nbf.v4.new_markdown_cell("## 演習4：実務向けプロンプトライブラリの作成"),
    nbf.v4.new_markdown_cell("### テンプレート例：契約書レビュー用プロンプト"),
    nbf.v4.new_code_cell('"""# 契約書レビュー・リスク分析プロンプト\n\n## 目的\n契約書の包括的なレビューを行い、法的リスクを特定し、改善提案を行う\n\n## 入力情報\n- 契約書全文\n..."""'),
]

# Add cells to notebook
nb['cells'] = cells

# Write the notebook to a file
notebook_path = '/home/ubuntu/repos/AI_Study/website/stage1/notebooks/exercises/prompt-engineering-answers.ipynb'
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

print(f"Notebook created at {notebook_path}")
