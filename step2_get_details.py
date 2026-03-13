import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"}

def get_repo_meta(repo_name):
    """获取仓库星级和描述"""
    url = f"https://api.github.com/repos/{repo_name}"
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            data = res.json()
            return {
                "stars": data.get("stargazers_count", 0),
                "description": data.get("description", "")
            }
    except:
        pass
    return {"stars": 0, "description": "N/A"}

def fetch_all_items(repo_name):
    """获取该仓库的 Issues 和 PRs"""
    issues = []
    prs = []
    # 抓取最近的 100 条记录（可调大）
    url = f"https://api.github.com/repos/{repo_name}/issues?state=all&per_page=100"
    
    try:
        res = requests.get(url, headers=HEADERS)
        if res.status_code == 200:
            items = res.json()
            for item in items:
                content = {
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "state": item.get("state"),
                    "labels": [l['name'] for l in item.get('labels', [])],
                    "created_at": item.get("created_at"),
                    "url": item.get("html_url"),
                    "body": item.get("body")[:1000] if item.get("body") else ""
                }
                
                # 区分 PR 和 Issue
                if "pull_request" in item:
                    prs.append(content)
                else:
                    issues.append(content)
    except:
        pass
    return issues, prs

def main():
    if not os.path.exists('data/repo_list.txt'):
        print("请先运行 step1 生成列表")
        return

    with open('data/repo_list.txt', 'r') as f:
        repos = [line.strip() for line in f.readlines()]

    final_data = {}

    for idx, repo in enumerate(repos):
        print(f"[{idx+1}/{len(repos)}] 正在深度抓取: {repo}")
        
        # 获取元数据
        meta = get_repo_meta(repo)
        
        # 获取内容
        issues, prs = fetch_all_items(repo)
        
        # 存入大字典
        final_data[repo] = {
            "stars": meta["stars"],
            "description": meta["description"],
            "total_issues_count": len(issues),
            "total_prs_count": len(prs),
            "issues": issues,
            "pull_requests": prs
        }
        
        # 每抓 10 个保存一次，防止程序崩溃
        if (idx + 1) % 10 == 0:
            with open("data/medical_ai_full_data.json", "w", encoding='utf-8') as f_json:
                json.dump(final_data, f_json, ensure_ascii=False, indent=2)

        time.sleep(1) # 频率控制

    # 最终保存
    with open("data/medical_ai_full_data.json", "w", encoding='utf-8') as f_json:
        json.dump(final_data, f_json, ensure_ascii=False, indent=2)
    
    print(f"\n全部完成！数据已打包至: data/medical_ai_full_data.json")

if __name__ == "__main__":
    main()