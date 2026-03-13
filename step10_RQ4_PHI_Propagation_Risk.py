import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 学术化设置
sns.set_theme(style="whitegrid", context="paper")
plt.rcParams['axes.unicode_minus'] = False 

def analyze_rq4_phi_risk():
    print("🚀 Starting RQ4: PHI Leakage & Boundary Propagation Risk Analysis...")
    
    with open("data/medical_ai_full_data.json", "r", encoding='utf-8') as f:
        data = json.load(f)

    records = []

    for repo, info in data.items():
        repo_type = "AI-Agent/LLM" if any(k in repo.lower() for k in ['agent', 'llm', 'gpt', 'med']) else "Traditional-OSS"
        
        # 整合文本分析背景
        text_content = (str(info.get('description', '')) + " " + 
                        str([pr.get('title', '') + pr.get('body', '') for pr in info.get('pull_requests', [])])).lower()
        
        # 维度 1: PHI 数据类型风险 (影像、日志、备份)
        phi_types = 0
        if any(w in text_content for w in ['dicom', 'image', 'mri', 'ct', 'x-ray']): phi_types += 1 # 影像
        if any(w in text_content for w in ['log', 'trace', 'history', 'chat_history']): phi_types += 1 # 日志/对话
        if any(w in text_content for w in ['dump', 'csv', 'backup', 'export', 'xlsx']): phi_types += 1 # 导出/备份
        
        # 维度 2: 接口与互操作性 (传播半径)
        # 评估是否连接外部 API、FHIR、HL7 或 Webhook
        propagation_radius = 0
        if any(w in text_content for w in ['api', 'external', 'request', 'post']): propagation_radius += 1
        if any(w in text_content for w in ['fhir', 'hl7', 'interoperability', 'dicom-web']): propagation_radius += 2 # 标准互操作接口权重更高
        if any(w in text_content for w in ['webhook', 'callback', 'cloud']): propagation_radius += 1

        # 维度 3: AI 特有流转风险 (向量化/外部 LLM 发送)
        ai_flow_risk = 0
        if repo_type == "AI-Agent/LLM":
            if any(w in text_content for w in ['embedding', 'vector', 'pinecone', 'milvus']): ai_flow_risk += 1.5
            if any(w in text_content for w in ['openai', 'claude', 'gemini', 'api_key']): ai_flow_risk += 2.0

        records.append({
            'type': repo_type,
            'phi_leakage_surface': phi_types,
            'propagation_radius': propagation_radius,
            'ai_specific_risk': ai_flow_risk,
            'total_phi_risk': phi_types + propagation_radius + ai_flow_risk
        })

    df = pd.DataFrame(records)
    
    # --- 图 1：传播半径对比 (Propagation Radius) ---
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df, x='type', y='propagation_radius', hue='type', palette="coolwarm", showfliers=False, legend=False)
    plt.title('RQ4: Data Propagation Radius (API & Interoperability)', fontsize=14)
    plt.ylabel('Connectivity/Propagation Score')
    plt.savefig('data/RQ4_Propagation_Radius.png', dpi=300)

    # --- 图 2：PHI 泄露风险面热力图分析 ---
    plt.figure(figsize=(8, 6))
    risk_summary = df.groupby('type')[['phi_leakage_surface', 'ai_specific_risk']].mean()
    sns.heatmap(risk_summary, annot=True, cmap="YlOrRd")
    plt.title('RQ4: PHI Leakage Surface vs AI Flow Risk', fontsize=14)
    plt.savefig('data/RQ4_Risk_Heatmap.png', dpi=300)

    print("✅ RQ4 Analysis Complete. PHI risk visuals generated.")

if __name__ == "__main__":
    analyze_rq4_phi_risk()