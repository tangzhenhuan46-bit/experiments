import requests
import time
import json
import os
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ================= 配置区 =================
GITHUB_TOKEN = "" 
# 如果你使用了 VPN，请取消下面两行的注释并填入你的代理端口（如 7890）
# PROXIES = {"http": "http://127.0.0.1:7890", "https": "http://127.0.0.1:7890"}
PROXIES = None 

HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
QUERIES = ["medical vulnerability", "healthcare security fix", "clinical bug patch", "hospital software fix"]
TARGET_COUNT = 3000
# ==========================================

def get_session():
    session = requests.Session()
    # 增加重试机制，应对网络不稳定的 SSLError
    retry = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session

def run_spider():
    session = get_session()
    results = []
    seen_urls = set()
    
    for query in QUERIES:
        if len(results) >= TARGET_COUNT: break
        page = 1
        print(f"正在检索: {query}")
        
        while page <= 15:
            search_url = f"https://api.github.com/search/issues?q={query}+is:pr+is:closed&per_page=100&page={page}"
            try:
                resp = session.get(search_url, headers=HEADERS, proxies=PROXIES, timeout=20)
                if resp.status_code == 403:
                    time.sleep(60); continue
                
                items = resp.json().get('items', [])
                if not items: break

                for item in items:
                    if item['html_url'] in seen_urls: continue
                    
                    # 获取核心治理元数据 (满足 RQ2 要求) [cite: 2]
                    record = {
                        'title': item.get('title'),
                        'body': item.get('body', ''), # 用于计算文本长度 [cite: 40]
                        'created_at': item.get('created_at'), # 用于修复滞后分析 [cite: 2]
                        'merged_at': item.get('closed_at'), 
                        'html_url': item['html_url'],
                        # 简单的项目类型判定
                        'project_type': 'AI-Agent' if any(x in (item.get('title') or '').lower() for x in ['ai', 'llm', 'agent']) else 'Traditional'
                    }
                    results.append(record)
                    seen_urls.add(item['html_url'])
                    
                    if len(results) % 100 == 0:
                        print(f"当前进度: {len(results)}/{TARGET_COUNT}")
                    if len(results) >= TARGET_COUNT: break
                
                time.sleep(1)
            except Exception as e:
                print(f"网络波动，稍后重试: {e}")
                time.sleep(5)
            page += 1
            if len(results) >= TARGET_COUNT: break

    with open('medical_ai_full_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print("采集成功！")

if __name__ == "__main__":
    run_spider()