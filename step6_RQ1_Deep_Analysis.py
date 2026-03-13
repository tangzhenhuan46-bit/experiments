import json
import pandas as pd
import re
from datetime import datetime

def run_rq1_analysis():
    with open("data/medical_ai_full_data.json", "r", encoding='utf-8') as f:
        data = json.load(f)

    results = []

    # 1. 定义更细致的分类词库
    CWE_DICT = {
        'CWE-200 (Privacy/PHI Leak)': r'privacy|leak|phi|hipaa|patient data|exposure',
        'CWE-20 (Improper Input)': r'injection|prompt injection|adversarial|jailbreak',
        'CWE-287 (Auth/Access)': r'unauthorized|login|authentication|access control',
        'CWE-399 (Resource/Model Failure)': r'hallucination|dos|timeout|crash|memory leak',
        'CWE-703 (Logic/Agent Error)': r'agent failed|logic error|planning error|tool failure'
    }

    for repo, info in data.items():
        stars = info.get('stars', 0)
        # 标记项目类型
        repo_type = "AI-Agent/LLM" if any(k in repo.lower() for k in ['agent', 'llm', 'gpt', 'med-']) else "Traditional-OSS"
        
        all_items = info.get('issues', []) + info.get('pull_requests', [])
        for item in all_items:
            text = (str(item['title']) + " " + str(item['body'])).lower()
            
            # 识别 CWE 类别
            found_cwe = "General Bug"
            for cwe_label, pattern in CWE_DICT.items():
                if re.search(pattern, text):
                    found_cwe = cwe_label
                    break
            
            # 计算严重度 (基于关键词组合)
            severity_score = 1 # Low
            if any(k in text for k in ['critical', 'vulnerability', 'exploit', 'security']):
                severity_score = 3 # High
            elif any(k in text for k in ['fix', 'error', 'wrong']):
                severity_score = 2 # Medium
            
            # 修正：大项目的小问题也可能由于用户基数大而变得严重
            if stars > 500 and severity_score < 3:
                severity_score += 1

            results.append({
                'repo': repo,
                'type': repo_type,
                'cwe': found_cwe,
                'severity': {1:'Low', 2:'Medium', 3:'High', 4:'Critical'}[severity_score],
                'date': pd.to_datetime(item['created_at']),
                'year': pd.to_datetime(item['created_at']).year
            })

    df = pd.DataFrame(results)
    df.to_csv("data/RQ1_final_landscape.csv", index=False, encoding='utf-8-sig')
    return df

if __name__ == "__main__":
    df = run_rq1_analysis()
    print(f"RQ1 数据处理完成，共分析 {len(df)} 条记录。")