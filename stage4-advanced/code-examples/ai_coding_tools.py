# AIコーディング支援ツールの活用例

import os
import re
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import openai
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

# 契約書テキストから重要情報を抽出する関数
def extract_contract_info(contract_text):
    """
    契約書テキストから重要な情報を抽出します。
    
    Parameters:
    contract_text (str): 契約書の全文
    
    Returns:
    dict: 抽出された情報を含む辞書
    """
    # 結果を格納する辞書
    results = {
        "parties": [],
        "effective_date": None,
        "expiration_date": None,
        "key_clauses": {},
        "risk_factors": []
    }
    
    # 契約当事者の抽出
    party_pattern = r"(甲|乙|丙|丁)[:：]?\s*([^、。\n]+)"
    party_matches = re.finditer(party_pattern, contract_text)
    for match in party_matches:
        party_role = match.group(1)
        party_name = match.group(2).strip()
        results["parties"].append({"role": party_role, "name": party_name})
    
    # 日付の抽出
    date_pattern = r"(\d{4})年(\d{1,2})月(\d{1,2})日"
    dates = re.findall(date_pattern, contract_text)
    if len(dates) >= 2:
        # 最初の日付を開始日とする（単純化のため）
        results["effective_date"] = f"{dates[0][0]}-{dates[0][1]}-{dates[0][2]}"
        # 最後の日付を終了日とする（単純化のため）
        results["expiration_date"] = f"{dates[-1][0]}-{dates[-1][1]}-{dates[-1][2]}"
    
    # 重要な条項の抽出
    key_clause_patterns = {
        "confidentiality": r"秘密保持|機密情報|守秘義務",
        "liability": r"責任制限|損害賠償|賠償責任",
        "governing_law": r"準拠法|管轄裁判所",
        "termination": r"解除|解約|終了"
    }
    
    for clause_type, pattern in key_clause_patterns.items():
        # 条項を含む段落を抽出
        clause_pattern = r"(第\d+条.*?" + pattern + r".*?。)"
        clause_matches = re.findall(clause_pattern, contract_text, re.DOTALL)
        if clause_matches:
            results["key_clauses"][clause_type] = clause_matches
    
    # リスク要因の特定（単純な例）
    risk_patterns = [
        r"違約金.*?(\d+)%",
        r"損害賠償.*?制限なく",
        r"自動更新",
        r"専属的合意管轄"
    ]
    
    for pattern in risk_patterns:
        risk_matches = re.findall(pattern, contract_text)
        if risk_matches:
            results["risk_factors"].append(pattern.replace(r".*?(\d+)%", "").replace(r".*?", ""))
    
    return results

# OpenAI APIを使用して契約書を分析する関数
def analyze_contract_with_ai(contract_text):
    """
    OpenAI APIを使用して契約書を分析します。
    
    Parameters:
    contract_text (str): 分析する契約書の全文
    
    Returns:
    str: AI分析の結果
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは法務アシスタントです。契約書を分析し、以下の情報を抽出してください：\n1. 契約当事者\n2. 契約期間\n3. 重要な条項（秘密保持、責任制限、準拠法など）\n4. 潜在的なリスク\n5. 改善提案"},
                {"role": "user", "content": f"以下の契約書を分析してください:\n\n{contract_text}"}
            ],
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

# 契約書の比較分析を行う関数
def compare_contracts(contract1_text, contract2_text):
    """
    2つの契約書を比較分析します。
    
    Parameters:
    contract1_text (str): 1つ目の契約書の全文
    contract2_text (str): 2つ目の契約書の全文
    
    Returns:
    dict: 比較分析の結果
    """
    # 各契約書から情報を抽出
    contract1_info = extract_contract_info(contract1_text)
    contract2_info = extract_contract_info(contract2_text)
    
    # 比較結果を格納する辞書
    comparison = {
        "parties_diff": {},
        "dates_diff": {},
        "clauses_diff": {},
        "risk_factors_diff": {}
    }
    
    # 当事者の比較
    contract1_parties = {party["role"]: party["name"] for party in contract1_info["parties"]}
    contract2_parties = {party["role"]: party["name"] for party in contract2_info["parties"]}
    
    all_roles = set(contract1_parties.keys()) | set(contract2_parties.keys())
    for role in all_roles:
        if role in contract1_parties and role in contract2_parties:
            if contract1_parties[role] != contract2_parties[role]:
                comparison["parties_diff"][role] = {
                    "contract1": contract1_parties[role],
                    "contract2": contract2_parties[role]
                }
        elif role in contract1_parties:
            comparison["parties_diff"][role] = {
                "contract1": contract1_parties[role],
                "contract2": "なし"
            }
        else:
            comparison["parties_diff"][role] = {
                "contract1": "なし",
                "contract2": contract2_parties[role]
            }
    
    # 日付の比較
    for date_type in ["effective_date", "expiration_date"]:
        if contract1_info[date_type] != contract2_info[date_type]:
            comparison["dates_diff"][date_type] = {
                "contract1": contract1_info[date_type],
                "contract2": contract2_info[date_type]
            }
    
    # 条項の比較
    all_clause_types = set(contract1_info["key_clauses"].keys()) | set(contract2_info["key_clauses"].keys())
    for clause_type in all_clause_types:
        if clause_type in contract1_info["key_clauses"] and clause_type in contract2_info["key_clauses"]:
            if contract1_info["key_clauses"][clause_type] != contract2_info["key_clauses"][clause_type]:
                comparison["clauses_diff"][clause_type] = {
                    "contract1": contract1_info["key_clauses"][clause_type],
                    "contract2": contract2_info["key_clauses"][clause_type]
                }
        elif clause_type in contract1_info["key_clauses"]:
            comparison["clauses_diff"][clause_type] = {
                "contract1": contract1_info["key_clauses"][clause_type],
                "contract2": "なし"
            }
        else:
            comparison["clauses_diff"][clause_type] = {
                "contract1": "なし",
                "contract2": contract2_info["key_clauses"][clause_type]
            }
    
    # リスク要因の比較
    contract1_risks = set(contract1_info["risk_factors"])
    contract2_risks = set(contract2_info["risk_factors"])
    
    comparison["risk_factors_diff"] = {
        "only_in_contract1": list(contract1_risks - contract2_risks),
        "only_in_contract2": list(contract2_risks - contract1_risks),
        "common": list(contract1_risks & contract2_risks)
    }
    
    return comparison

# 契約書の自動生成を行う関数
def generate_contract_template(contract_type, party1, party2, effective_date, expiration_date, additional_clauses=None):
    """
    指定されたパラメータに基づいて契約書のテンプレートを生成します。
    
    Parameters:
    contract_type (str): 契約書の種類（例: "秘密保持契約", "業務委託契約"）
    party1 (str): 甲の名称
    party2 (str): 乙の名称
    effective_date (str): 契約開始日（YYYY-MM-DD形式）
    expiration_date (str): 契約終了日（YYYY-MM-DD形式）
    additional_clauses (list, optional): 追加したい特別条項のリスト
    
    Returns:
    str: 生成された契約書テンプレート
    """
    try:
        # 日付のフォーマット変換
        effective_date_obj = datetime.strptime(effective_date, "%Y-%m-%d")
        expiration_date_obj = datetime.strptime(expiration_date, "%Y-%m-%d")
        
        effective_date_jp = effective_date_obj.strftime("%Y年%m月%d日")
        expiration_date_jp = expiration_date_obj.strftime("%Y年%m月%d日")
        
        # 追加条項の処理
        additional_clauses_text = ""
        if additional_clauses:
            additional_clauses_text = "追加条項：\n" + "\n".join([f"- {clause}" for clause in additional_clauses])
        
        # OpenAI APIを使用して契約書テンプレートを生成
        prompt = f"""
        以下の情報に基づいて{contract_type}のテンプレートを日本語で作成してください：
        
        - 契約当事者：
          甲: {party1}
          乙: {party2}
        - 契約期間：{effective_date_jp}から{expiration_date_jp}まで
        {additional_clauses_text}
        
        法的に適切な形式で、一般的な条項（目的、義務、秘密保持、責任制限、解除、準拠法など）を含めてください。
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは法務専門家です。正確で法的に適切な契約書テンプレートを作成してください。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"契約書テンプレートの生成中にエラーが発生しました: {str(e)}"

# メイン処理
if __name__ == "__main__":
    print("AIコーディング支援ツールの活用例")
    print("=" * 50)
    
    # サンプル契約書テキスト
    sample_contract = """
    秘密保持契約書
    
    甲：株式会社法務テック
    乙：株式会社AIソリューションズ
    
    第1条（目的）
    本契約は、甲乙間の業務提携に関連して開示される秘密情報の取扱いを定めることを目的とする。
    
    第2条（秘密情報）
    本契約において秘密情報とは、甲または乙が相手方に開示する技術上、営業上の情報であって、秘密である旨を明示したものをいう。
    
    第3条（秘密保持義務）
    甲および乙は、相手方から開示された秘密情報を厳に秘密として保持し、第三者に開示または漏洩してはならない。
    
    第4条（損害賠償）
    本契約に違反して秘密情報を漏洩した場合、違反当事者は相手方に対して、一切の損害を賠償する責任を負う。
    
    第5条（契約期間）
    本契約は、2023年4月1日から2024年3月31日までとする。ただし、期間満了の1ヶ月前までに甲乙いずれからも書面による異議がない場合は、自動的に1年間延長されるものとする。
    
    第6条（準拠法および管轄裁判所）
    本契約の準拠法は日本法とし、本契約に関する紛争については東京地方裁判所を第一審の専属的合意管轄裁判所とする。
    
    以上、本契約の成立を証するため、本書2通を作成し、甲乙記名押印の上、各1通を保有する。
    
    2023年4月1日
    
    甲：東京都千代田区丸の内1-1-1
    　　株式会社法務テック
    　　代表取締役 法務 太郎
    
    乙：東京都港区六本木6-6-6
    　　株式会社AIソリューションズ
    　　代表取締役 AI 次郎
    """
    
    # 1. 契約書情報の抽出
    print("\n1. 契約書情報の抽出")
    print("-" * 50)
    contract_info = extract_contract_info(sample_contract)
    print(json.dumps(contract_info, indent=2, ensure_ascii=False))
    
    # 2. AI分析
    print("\n2. AI分析")
    print("-" * 50)
    ai_analysis = analyze_contract_with_ai(sample_contract)
    print(ai_analysis)
    
    # 3. 契約書テンプレートの生成
    print("\n3. 契約書テンプレートの生成")
    print("-" * 50)
    template = generate_contract_template(
        contract_type="業務委託契約",
        party1="株式会社法務テック",
        party2="株式会社AIソリューションズ",
        effective_date="2023-05-01",
        expiration_date="2024-04-30",
        additional_clauses=["成果物の著作権は甲に帰属する", "月額報酬は50万円とする"]
    )
    print(template) 