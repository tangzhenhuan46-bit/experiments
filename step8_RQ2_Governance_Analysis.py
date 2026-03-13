import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 1. 初始化设置：使用学术常用风格
sns.set_theme(style="whitegrid", context="paper")
plt.rcParams['axes.unicode_minus'] = False 

def analyze_rq2_academic():
    print("🚀 Starting RQ2 Academic Analysis (Governance Transparency & Complexity)...")
    
    file_path = "data/medical_ai_full_data.json"
    if not os.path.exists(file_path):
        print(f"❌ Error: Cannot find {file_path}")
        return

    with open(file_path, "r", encoding='utf-8') as f:
        data = json.load(f)

    records = []
    # 扩大治理行为的识别关键词
    keywords = ['add', 'update', 'fix', 'paper', 'readme', 'agent', 'reasoning', 'security', 'bug', 'patch']

    for repo, info in data.items():
        # 分类逻辑
        repo_type = "AI-Agent/LLM" if any(k in repo.lower() for k in ['agent', 'llm', 'gpt', 'med']) else "Traditional-OSS"
        
        # 提取数据：重点分析 Pull Requests (治理的主要载体)
        prs = info.get('pull_requests', [])
        
        for pr in prs:
            # 只要是已关闭的 PR，均视为一次治理交互
            if pr.get('state') == 'closed':
                title = str(pr.get('title', '')).lower()
                body = str(pr.get('body', '') or '').lower()
                
                # 只有包含关键词的 PR 才被计入安全治理统计
                if any(k in (title + " " + body) for k in keywords):
                    records.append({
                        'type': repo_type,
                        'title_len': len(title),
                        'body_len': len(body),
                        'has_description': 1 if len(body) > 0 else 0
                    })

    df = pd.DataFrame(records)
    
    if df.empty:
        print("❌ No matching governance data found.")
        return

    print(f"✅ Successfully aligned {len(df)} governance records.")

    # --- Figure 1: Governance Transparency (PR Description Ratio) ---
    # 理论支撑：验证论文二中的“隐秘修复”与“社区透明感知”
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x='type', y='has_description', hue='type', palette="viridis", legend=False)
    
    plt.title('RQ2: Governance Transparency (PR Description Fill-rate)', fontsize=14, pad=15)
    plt.xlabel('Software Category', fontsize=12)
    plt.ylabel('Ratio of PRs with Detailed Body', fontsize=12)
    plt.ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig('data/RQ2_Transparency_Final.png', dpi=300)
    print("Saved: data/RQ2_Transparency_Final.png")

    # --- Figure 2: Repair Complexity (Body Length Distribution) ---
    # 理论支撑：验证论文一中的“业务逻辑鸿沟”导致的修复沟通成本
    plt.figure(figsize=(8, 6))
    # 使用 log 坐标系，因为 Body 长度差异可能极大，log 能更科学地展示分布
    sns.boxplot(data=df, x='type', y='body_len', hue='type', showfliers=False, palette="Set2", legend=False)
    
    plt.title('RQ2: Repair Complexity Assessment (Description Length)', fontsize=14, pad=15)
    plt.xlabel('Software Category', fontsize=12)
    plt.ylabel('Character Length (Body Content)', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('data/RQ2_Complexity_Final.png', dpi=300)
    print("Saved: data/RQ2_Complexity_Final.png")

    # 保存清洗后的数据供进一步分析
    df.to_csv("data/RQ2_Governance_Final_Data.csv", index=False)
    print("✅ All academic visuals generated successfully.")

if __name__ == "__main__":
    analyze_rq2_academic()