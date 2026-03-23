import requests
import time
import json
import os

# ================= 配置区 =================
GITHUB_TOKEN = ""
PROXIES = None # 如果网络报错，请设置为 {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

# 针对 RQ4 的精准搜索词：聚焦 PHI 流动与边界传播
QUERIES = [
    "medical PHI leak", "healthcare data export", "clinical API security",
    "HIPAA violation fix", "patient data transfer", "PACS DICOM leak",
    "hospital interoperability security", "HL7 FHIR security fix"
]
TARGET_COUNT = 3000
# ==========================================

def run_collector():
    results = []
    seen_urls = set()
    
    for q in QUERIES:
        if len(results) >= TARGET_COUNT: break
        print(f"正在检索风险维度: {q}")
        for page in range(1, 11): 
            try:
                url = f"https://api.github.com/search/issues?q={q}+is:pr+is:closed&per_page=100&page={page}"
                resp = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=20)
                if resp.status_code != 200: break
                
                items = resp.json().get('items', [])
                for item in items:
                    if item['html_url'] in seen_urls: continue
                    # 预提取 RQ4 关键字段
                    record = {
                        'title': item.get('title'),
                        'body': item.get('body', ''),
                        'repo': item.get('repository_url'),
                        'labels': [l['name'] for l in item.get('labels', [])],
                        'project_type': 'AI-Agent' if 'agent' in q or 'ai' in q else 'Traditional'
                    }
                    results.append(record)
                    seen_urls.add(item['html_url'])
                    if len(results) >= TARGET_COUNT: break
                time.sleep(1)
            except: continue
            if len(results) >= TARGET_COUNT: break

    with open('rq4_raw_leakage_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(f"RQ4 数据采集完成，共 {len(results)} 条记录。")

if __name__ == "__main__":
    run_collector()