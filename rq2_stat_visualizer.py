import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def generate_plots(csv_file):
    df = pd.read_csv(csv_file)
    sns.set(style="whitegrid")

    # 1. 披露路径对比图 (Discovery Path Distribution)
    plt.figure(figsize=(10, 6))
    path_counts = df.groupby(['project_type', 'discovery_path']).size().reset_index(name='count')
    sns.barplot(data=path_counts, x='discovery_path', y='count', hue='project_type')
    plt.title("Vulnerability Discovery Path: AI-Agent vs Traditional")
    plt.savefig('output/figures/fig_2a_discovery_paths.png')
    
    # 2. 修复手段占比 (Remediation Strategy)
    # 展开多选的动作
    df_exploded = df.assign(remediation_actions=df['remediation_actions'].str.split('|')).explode('remediation_actions')
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df_exploded, x='remediation_actions', hue='project_type')
    plt.xticks(rotation=45)
    plt.title("Remediation Strategies Distribution")
    plt.tight_layout()
    plt.savefig('output/figures/fig_2b_remediation_strategies.png')

    # 3. 修复滞后分析 (Repair Lag)
    plt.figure(figsize=(8, 6))
    sns.boxplot(data=df[df['repair_lag_days'] < 30], x='project_type', y='repair_lag_days')
    plt.title("Repair Lag (Days) - Within 30 Days")
    plt.savefig('output/figures/fig_2c_repair_lag.png')

if __name__ == "__main__":
    generate_plots('output/rq2_refined_governance_data.csv')
    print("图表已生成至 output/figures/ 文件夹")