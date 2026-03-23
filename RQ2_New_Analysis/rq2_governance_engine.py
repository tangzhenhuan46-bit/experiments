import re
import json
import pandas as pd
from datetime import datetime

class RQ2GovernanceEngine:
    def __init__(self, input_path):
        print(f"正在加载数据: {input_path}...")
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                # 兼容性处理：如果 JSON 最外层是字典且数据在某个 key 下，或者直接是列表
                if isinstance(content, dict):
                    # 尝试寻找可能的列表字段，如果找不到则把字典变成列表
                    self.raw_data = content.get('data', content.get('RECORDS', [content]))
                    if not isinstance(self.raw_data, list):
                        self.raw_data = [content]
                else:
                    self.raw_data = content
            print(f"成功加载 {len(self.raw_data)} 条原始记录。")
        except Exception as e:
            print(f"文件读取失败: {e}")
            self.raw_data = []
        
        self.path_rules = {
            'Official_Advisory': r'(cve-\d{4}-\d+|ghsa-\w+-\w+|security advisory|vulnerability report)',
            'Community_Report': r'(reported by|found by|thanks to|discovery by|bug bounty|external report)',
            'Internal_Audit': r'(static analysis|linter|fuzzer|unit test|ci failed|sonarqube|automated scan)'
        }
        
        self.strategy_rules = {
            'Logic_Patching': r'(logic|refactor|algorithm|validation|check|overflow|sanitize|fix bug)',
            'Config_Hardening': r'(docker|compose|env|port|settings|permission|yml|yaml|config)',
            'Semantic_Alignment': r'(prompt|llm|instruction|temperature|template|hallucination|agent logic)', 
            'Defensive_Doc': r'(warning|caution|documentation|readme|note|guide|manual update)'
        }

    def clean_semantic_text(self, text):
        if not text or not isinstance(text, str): return ""
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'(traceback|exception|error message|stack trace).*?(\n\s*\n|$)', '', text, flags=re.I | re.DOTALL)
        text = re.sub(r'http\S+', '', text)
        return text.strip()

    def parse_date(self, date_str):
        if not date_str or not isinstance(date_str, str): return None
        for fmt in ('%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S'):
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        return None

    def run(self):
        results = []
        for index, item in enumerate(self.raw_data):
            # 关键修复：确保 item 是字典格式，跳过字符串或其他类型
            if not isinstance(item, dict):
                # print(f"跳过非字典格式记录 (Index: {index})")
                continue

            body = item.get('body', '')
            clean_body = self.clean_semantic_text(body)
            title = str(item.get('title', '')).lower()
            content = (title + " " + clean_body).lower()

            path = "Silent_Commit"
            for label, pattern in self.path_rules.items():
                if re.search(pattern, content):
                    path = label
                    break
            
            actions = [label for label, pattern in self.strategy_rules.items() if re.search(pattern, content)]
            
            c_at = self.parse_date(item.get('created_at'))
            m_at = self.parse_date(item.get('merged_at'))
            lag = (m_at - c_at).days if (c_at and m_at) else None

            results.append({
                'project_type': item.get('project_type', 'Traditional'),
                'discovery_path': path,
                'remediation_actions': "|".join(actions) if actions else "Standard_Fix",
                'repair_lag_days': lag,
                'clean_body_len': len(clean_body)
            })
        
        return pd.DataFrame(results)

if __name__ == "__main__":
    import os
    if not os.path.exists('output'): os.makedirs('output')
    
    # 请确保 medical_ai_full_data.json 就在 rq2_governance_engine.py 旁边
    input_file = 'medical_ai_full_data.json' 
    if os.path.exists(input_file):
        engine = RQ2GovernanceEngine(input_file)
        df = engine.run()
        if not df.empty:
            df.to_csv('output/rq2_refined_results.csv', index=False)
            print(f"分析完成！共提取有效治理记录 {len(df)} 条。")
        else:
            print("未能提取到任何有效数据，请检查 JSON 字段名是否包含 'body', 'title' 等。")
    else:
        print(f"错误：找不到文件 {input_file}。请检查文件路径。")