import nbformat as nbf
import os

# Create a new notebook for ChatGPT basics
def create_chatgpt_basics_notebook():
    nb = nbf.v4.new_notebook()
    
    cells = [
        nbf.v4.new_markdown_cell("# ChatGPT基本操作演習 - 模範解答\n\nこのノートブックでは、ChatGPT基本操作演習の模範解答と解説を提供します。各演習を通じて得られる知見と、法務業務におけるAI活用の可能性について理解を深めましょう。"),
        
        # 演習1：基本的な質問応答
        nbf.v4.new_markdown_cell("## 演習1：基本的な質問応答\n\nこの演習では、基本的な法務関連の質問をChatGPTに投げかけ、その回答の質と正確性を評価します。"),
        
        # 質問例と回答例（省略）
        nbf.v4.new_markdown_cell("### 質問例と回答例"),
        nbf.v4.new_code_cell('"""個人情報保護法の主な目的を教えてください"""'),
        nbf.v4.new_markdown_cell("#### 回答例と考察"),
        nbf.v4.new_markdown_cell("個人情報保護法の目的に関する回答例と、ChatGPTの回答の正確性、網羅性、構造化について考察します。"),
        
        # 演習2：会話の継続と文脈理解
        nbf.v4.new_markdown_cell("## 演習2：会話の継続と文脈理解\n\nこの演習では、一連の質問を通じてChatGPTの文脈理解能力と会話の継続性を検証します。"),
        
        # 会話例と考察（省略）
        nbf.v4.new_markdown_cell("### 会話例：民法改正に関する一連の質問"),
        nbf.v4.new_code_cell('"""民法の改正点について教えてください"""'),
        nbf.v4.new_markdown_cell("#### 会話の流れと考察"),
        nbf.v4.new_markdown_cell("民法改正に関する一連の質問と回答を通じて、ChatGPTの文脈維持能力と情報の深化について考察します。"),
        
        # 演習3：指示の明確化と修正
        nbf.v4.new_markdown_cell("## 演習3：指示の明確化と修正\n\nこの演習では、指示の明確化と修正を通じて、より適切な成果物を得るためのプロンプト改善方法を学びます。"),
        
        # 指示例と修正例（省略）
        nbf.v4.new_markdown_cell("### 指示例：雇用契約書の作成"),
        nbf.v4.new_code_cell('"""雇用契約書のサンプルを作成してください"""'),
        nbf.v4.new_markdown_cell("#### 指示の明確化と結果の変化"),
        nbf.v4.new_markdown_cell("基本的な指示から、より具体的な要件を追加することで、成果物がどのように変化するかを考察します。"),
        
        # 演習4：異なるモデルの比較
        nbf.v4.new_markdown_cell("## 演習4：異なるモデルの比較\n\nこの演習では、GPT-3.5とGPT-4の回答の違いを比較し、法務業務におけるAIモデル選択の重要性を理解します。"),
        
        # モデル比較例（省略）
        nbf.v4.new_markdown_cell("### 比較例：法務デューデリジェンスのチェックポイント"),
        nbf.v4.new_code_cell('"""M&A取引における法務デューデリジェンスの主要なチェックポイントを10項目リストアップし、各項目について簡潔に説明してください"""'),
        nbf.v4.new_markdown_cell("#### モデル間の違いと実務的意義"),
        nbf.v4.new_markdown_cell("GPT-3.5とGPT-4の回答の違いを分析し、法務業務における適切なモデル選択の重要性について考察します。"),
        
        # 演習5：限界の理解
        nbf.v4.new_markdown_cell("## 演習5：限界の理解\n\nこの演習では、ChatGPTの限界を理解し、法務業務で活用する際の注意点を学びます。"),
        
        # 限界例と対策（省略）
        nbf.v4.new_markdown_cell("### 限界例：最新の法改正や判例"),
        nbf.v4.new_code_cell('"""2023年以降に施行された個人情報保護法の改正点について教えてください"""'),
        nbf.v4.new_markdown_cell("#### 限界の理解と対策"),
        nbf.v4.new_markdown_cell("ChatGPTの知識の時間的制約や法的正確性の限界を理解し、法務業務で活用する際の適切な対策について考察します。"),
        
        # まとめ
        nbf.v4.new_markdown_cell("## まとめ：法務業務におけるChatGPTの効果的な活用法\n\n以上の演習を通じて得られた知見をもとに、法務業務でChatGPTを効果的に活用するためのベストプラクティスをまとめます。"),
        nbf.v4.new_markdown_cell("""
1. **適切な用途の選択**：基本的な法的知識の確認や文書の初期ドラフト作成など、ChatGPTの強みを活かせる業務に活用する

2. **プロンプト設計の工夫**：具体的で明確な指示を出し、必要に応じて段階的に情報を深化させる

3. **出力内容の検証**：ChatGPTの回答は必ず法務専門家が検証し、最新の法改正や判例を反映させる

4. **適切なモデル選択**：タスクの複雑さや重要度に応じて、適切なモデル（GPT-3.5/GPT-4）を選択する

5. **限界の認識と補完**：ChatGPTの限界（最新情報、法的解釈の正確性など）を理解し、適切に人間の専門知識で補完する
""")
    ]
    
    # Add cells to notebook
    nb['cells'] = cells
    
    # Write the notebook to a file
    notebook_path = '/home/ubuntu/repos/AI_Study/website/stage1/notebooks/exercises/chatgpt-basics-answers.ipynb'
    with open(notebook_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    
    print(f"Notebook created at {notebook_path}")

# Execute the function to create the notebook
if __name__ == "__main__":
    create_chatgpt_basics_notebook()
