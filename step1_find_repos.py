import os
import requests
import time
from dotenv import load_dotenv

# 加载配置
load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"}

# --- 核心配置：精准的AI医疗关键词与主题 ---
# 1. 主题搜索 (GitHub Topics 是最精准的分类)
TOPICS = [
    'medical-llm', 'clinical-llm', 'medical-agent', 
    'healthcare-ai', 'medical-nlp', 'biomedical-ai'
]

# 2. 关键词搜索 (涵盖Agent、漏洞、医疗模型)
KEYWORDS = [
    'AI medical agent', 'healthcare LLM vulnerability',
    'clinical agent bug', 'medical data privacy AI',
    'Med-PALM', 'BioGPT', 'HealthGPT'
]

# 3. 知名医疗AI组织 (直接抓取他们的所有仓库)
ORGS = ['AgenticHealthAI', 'mims-harvard', 'FreedomIntelligence', 'Google-Health']

def find_all_repos():
    all_found_repos = set()
    
    # --- A. 搜索 Topics ---
    for topic in TOPICS:
        print(f"正在抓取主题: {topic}...")
        url = f"https://api.github.com/search/repositories?q=topic:{topic}&per_page=100"
        try:
            res = requests.get(url, headers=HEADERS)
            if res.status_code == 200:
                items = res.json().get('items', [])
                for item in items:
                    all_found_repos.add(item['full_name'])
            time.sleep(2) # 避开频率限制
        except Exception as e:
            print(f"抓取主题 {topic} 出错: {e}")

    # --- B. 搜索 关键词 ---
    for kw in KEYWORDS:
        print(f"正在搜索关键词: {kw}...")
        url = f"https://api.github.com/search/repositories?q={kw}&per_page=100"
        try:
            res = requests.get(url, headers=HEADERS)
            if res.status_code == 200:
                items = res.json().get('items', [])
                for item in items:
                    all_found_repos.add(item['full_name'])
            time.sleep(2)
        except Exception as e:
            print(f"搜索关键词 {kw} 出错: {e}")

    # --- C. 抓取 特定机构 ---
    for org in ORGS:
        print(f"正在检查组织: {org}...")
        url = f"https://api.github.com/orgs/{org}/repos?per_page=100"
        try:
            res = requests.get(url, headers=HEADERS)
            if res.status_code == 200:
                repos = res.json()
                for r in repos:
                    all_found_repos.add(r['full_name'])
        except Exception as e:
            print(f"抓取机构 {org} 出错: {e}")

    # --- 保存结果 ---
    if not os.path.exists('data'):
        os.makedirs('data')
        
    with open("data/repo_list.txt", "w", encoding='utf-8') as f:
        for repo in sorted(list(all_found_repos)):
            f.write(repo + "\n")
            
    print(f"\n--- 挖掘结束 ---")
    print(f"总计找到 {len(all_found_repos)} 个相关的AI医疗仓库名。")
    print(f"结果已保存至: data/repo_list.txt")

if __name__ == "__main__":
    find_all_repos()