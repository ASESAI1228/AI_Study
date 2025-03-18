# テキスト処理の練習

# 1. 以下の契約書条項を定義してください
clause = """
第10条（秘密保持）
1. 甲および乙は、本契約に関連して知り得た相手方の技術上・営業上の一切の情報（以下「秘密情報」という）を、相手方の事前の書面による承諾なく第三者に開示または漏洩してはならない。
2. 前項の規定にかかわらず、次の各号のいずれかに該当する情報については、秘密情報から除外するものとする。
   (1) 開示を受けた際、既に公知となっていた情報
   (2) 開示を受けた際、既に自己が保有していた情報
   (3) 開示を受けた後、自己の責によらず公知となった情報
   (4) 正当な権限を有する第三者から適法に取得した情報
   (5) 相手方から開示された情報によらず、独自に開発した情報
3. 本条の規定は、本契約終了後も3年間効力を有するものとする。
"""

# 2. 上記の条項から、以下の情報を抽出して表示してください
# - 条項のタイトル
# - 秘密情報の定義
# - 秘密情報から除外される項目のリスト
# - 秘密保持義務の有効期間

import re

# タイトルの抽出
title_match = re.search(r"第\d+条（(.+?)）", clause)
if title_match:
    title = title_match.group(1)
    print(f"条項のタイトル: {title}")

# 秘密情報の定義を抽出
definition_match = re.search(r"「秘密情報」という\）(.+?)を", clause)
if definition_match:
    definition = definition_match.group(1).strip()
    print(f"秘密情報の定義: {definition}")

# 除外項目を抽出
exclusions = re.findall(r"\(\d+\) (.+?)$", clause, re.MULTILINE)
print("\n秘密情報から除外される項目:")
for item in exclusions:
    print(f"- {item}")

# 有効期間を抽出
period_match = re.search(r"本契約終了後も(\d+)年間", clause)
if period_match:
    period = period_match.group(1)
    print(f"\n秘密保持義務の有効期間: {period}年間")

# 3. 上記の条項を、以下のように修正してください
# - 「甲および乙」を「甲、乙および丙」に変更
# - 有効期間を3年から5年に変更
modified_clause = clause.replace("甲および乙", "甲、乙および丙")
modified_clause = re.sub(r"本契約終了後も3年間", "本契約終了後も5年間", modified_clause)

print("\n修正後の条項:")
print(modified_clause)

# 4. 修正後の条項の単語数をカウントして表示してください
words = re.findall(r'\w+', modified_clause)
print(f"\n修正後の条項の単語数: {len(words)}") 