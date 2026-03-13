import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 学术化设置
sns.set_theme(style="whitegrid", context="paper")
plt.rcParams['axes.unicode_minus'] = False 

def analyze_rq3_deployment():
    print("🚀 Starting RQ3: Default Deployment & Configuration Risk Scan...")
    
    with open("data/medical_ai_full_data.json", "r", encoding='utf-8') as f:
        data = json.load(f)

    records = []

    for repo, info in data.items():
        repo_type = "AI-Agent/LLM" if any(k in repo.lower() for k in ['agent', 'llm', 'gpt', 'med']) else "Traditional-OSS"
        
        # 模拟扫描项目中的配置文件痕迹 (基于 Description 和 Issue/PR 讨论)
        text_content = (str(info.get('description', '')) + " " + 
                        str([pr.get('title', '') + pr.get('body', '') for pr in info.get('pull_requests', [])])).lower()
        
        # 维度 1: 容器化攻击面 (Docker/Ports)
        has_docker = 1 if 'docker' in text_content else 0
        exposed_ports = 1 if any(p in text_content for p in ['port', '8080', '5000', '8000', 'expose']) else 0
        
        # 维度 2: 凭证暴露风险 (API Keys/Env)
        env_risk = 1 if any(k in text_content for k in ['api_key', 'env', 'secret', 'token', 'credentials']) else 0
        
        # 维度 3: 部署引导的脆弱性 (Quickstart/Usage)
        quickstart_risk = 1 if any(q in text_content for q in ['quickstart', 'setup', 'installation', 'run this']) else 0

        records.append({
            'type': repo_type,
            'docker_exposure': has_docker + exposed_ports,
            'credential_risk': env_risk,
            'deployment_complexity': quickstart_risk,
            'attack_surface_score': (has_docker + exposed_ports + env_risk)
        })

    df = pd.DataFrame(records)
    
    # --- 图 1：默认攻击面分值分布 (Attack Surface Score) ---
    plt.figure(figsize=(8, 6))
    sns.kdeplot(data=df, x='attack_surface_score', hue='type', fill=True, common_norm=False, palette="viridis")
    plt.title('RQ3: Distribution of Default Attack Surface Scores', fontsize=14)
    plt.xlabel('Attack Surface Score (Docker + Ports + Env Risks)')
    plt.savefig('data/RQ3_Attack_Surface_KDE.png', dpi=300)

    # --- 图 2：高风险配置项占比对比 ---
    # 统计各类型中 credential_risk 为 1 的比例
    plt.figure(figsize=(8, 6))
    risk_stats = df.groupby('type')['credential_risk'].mean().reset_index()
    sns.barplot(data=risk_stats, x='type', y='credential_risk', palette="magma")
    plt.title('RQ3: Ratio of Projects with Potential Credential Risks', fontsize=14)
    plt.ylabel('Ratio of API/Key Configuration Mentions')
    plt.savefig('data/RQ3_Credential_Ratio.png', dpi=300)

    print("✅ RQ3 Scan Complete. Deployment risk visuals generated.")

if __name__ == "__main__":
    analyze_rq3_deployment()