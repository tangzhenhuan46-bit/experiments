import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def plot_rq2_results(csv_path):
    if not os.path.exists(csv_path):
        print("错误：找不到分析结果CSV文件。")
        return

    df = pd.read_csv(csv_path)
    # 过滤掉异常的时间数据
    df = df[(df['repair_lag_days'] >= 0) | (df['repair_lag_days'].isna())]
    
    sns.set_theme(style="whitegrid", font_scale=1.2)
    if not os.path.exists('output/figures'): os.makedirs('output/figures')

    # 图 1: 披露路径分布 (横向)
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df, y='discovery_path', hue='project_type', palette='Set2')
    plt.title('Vulnerability Discovery Paths Analysis')
    plt.xlabel('Number of Cases')
    plt.tight_layout()
    plt.savefig('output/figures/discovery_paths.png')
    print("已生成：output/figures/discovery_paths.png")

    # 图 2: 治理手段占比
    df_exploded = df.assign(remediation_actions=df['remediation_actions'].str.split('|')).explode('remediation_actions')
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df_exploded, x='remediation_actions', hue='project_type', palette='muted')
    plt.title('Remediation Strategies Distribution (Empirical Actions)')
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig('output/figures/remediation_strategies.png')
    print("已生成：output/figures/remediation_strategies.png")

    # 图 3: 响应滞后箱线图
    plt.figure(figsize=(8, 7))
    sns.boxplot(data=df[df['repair_lag_days'] < 60], x='project_type', y='repair_lag_days', palette='pastel')
    plt.title('Repair Lag Comparison (Days)')
    plt.savefig('output/figures/repair_lag.png')
    print("已生成：output/figures/repair_lag.png")

if __name__ == "__main__":
    plot_rq2_results('output/rq2_refined_results.csv')