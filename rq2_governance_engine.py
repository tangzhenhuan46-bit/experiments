import re
import json
import pandas as pd
from datetime import datetime

class RQ2GovernanceEngine:
    def __init__(self, input_file):
        with open(input_file, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)
        
        # 定义正则：披露路径识别 (Discovery Path)
        self.path_patterns = {
            'Official_Advisory': r'(cve-\d{4}-\d+|ghsa-\w+-\w+|security advisory)',
            'Community_Report': r'(reported by|found by|thanks to|discovery by|bug bounty)',
            'Internal_Audit': r'(static analysis|linter|fuzzer|unit test|ci failed|sonarqube)',
        }
        
        # 定义正则：修复手段识别 (Remediation Strategy) - 解决“捏造名词”问题
        self.strategy_patterns = {
            'Logic_Fix': r'(logic|refactor|algorithm|validation|check|overflow|sanitize)',
            'Config_Hardening': r'(docker|compose|env|port|settings|permission|yml)',
            'Semantic_Alignment': r'(prompt|llm|instruction|temperature|template|hallucination)', # AI特有动作
            'Doc_Mitigation': r'(warning|caution|documentation|readme|note|guide)'
        }

    def clean_text(self, text):
        """语义降噪：剔除代码块和Log日志，回应马老师质疑"""
        if not text: return ""
        # 剔除 Markdown 代码块 (```...```)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        # 剔除常见的 Traceback 日志
        text = re.sub(r'traceback \(most recent call last\):.*?\n\S+', '', text, flags=re.IGNORECASE | re.DOTALL)
        return text.lower()

    def analyze(self):
        processed_list = []
        for item in self.raw_data:
            # 1. 基础信息
            raw_body = item.get('body', '')
            clean_body = self.clean_text(raw_body)
            title = item.get('title', '').lower()
            content = title + " " + clean_body
            
            # 2. 识别披露路径
            found_path = "Silent_Fix"
            for label, pattern in self.path_patterns.items():
                if re.search(pattern, content):
                    found_path = label
                    break
            
            # 3. 识别修复手段
            actions = []
            for label, pattern in self.strategy_patterns.items():
                if re.search(pattern, content):
                    actions.append(label)
            
            # 4. 计算治理周期 (Lag)
            try:
                created = datetime.strptime(item['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                merged = datetime.strptime(item['merged_at'], '%Y-%m-%dT%H:%M:%SZ')
                lag_days = (merged - created).days
            except:
                lag_days = None

            processed_list.append({
                'project_type': item.get('project_type'), # AI-Agent 或 Traditional
                'discovery_path': found_path,
                'remediation_actions': "|".join(actions) if actions else "Unspecified",
                'repair_lag_days': lag_days,
                'content_length_pure': len(clean_body) # 这是清洗后的长度，更具说服力
            })
        
        return pd.DataFrame(processed_list)

# 执行分析并保存结果
if __name__ == "__main__":
    # 注意：这里换成你真实的原始文件名
    engine = RQ2GovernanceEngine('medical_ai_full_data.json')
    result_df = engine.analyze()
    result_df.to_csv('output/rq2_refined_governance_data.csv', index=False)
    print("分析完成，结果已保存至 output/rq2_refined_governance_data.csv")