import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

def generate_hard_metrics_plots(json_path):
    # 1. 加载原始 JSON 数据
    print(f"正在读取原始数据: {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 转换为 DataFrame 并确保必要字段存在
    df = pd.DataFrame(data)
    
    # 数据预处理
    df['project_type'] = df.get('project_type', 'Traditional').fillna('Traditional')
    
    # 计算修复时长 (Repair Lag)
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['merged_at'] = pd.to_datetime(df['merged_at'], errors='coerce')
    df['repair_lag_days'] = (df['merged_at'] - df['created_at']).dt.days
    df = df.dropna(subset=['repair_lag_days']) # 剔除无法计算时间的异常值

    # --- 指标 1: PR 响应滞后熵 (Response Lag Entropy) ---
    # 计算变异系数 CV = std / mean
    lag_stats = df.groupby('project_type')['repair_lag_days'].agg(['mean', 'std']).reset_index()
    lag_stats['CV'] = lag_stats['std'] / lag_stats['mean']
    
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    sns.barplot(data=lag_stats, x='project_type', y='CV', hue='project_type', palette='viridis', legend=False)
    plt.title('Vulnerability Response Lag Entropy (CV)', fontsize=14)
    plt.ylabel('Coefficient of Variation (Higher = Less Predictable)')
    plt.savefig('output/metric_1_entropy.png')
    
    # --- 指标 2: 治理动作离散度 (Action Dispersity) ---
    # 根据标题和正文关键词模拟治理动作的多样性
    def count_actions(text):
        if not isinstance(text, str): return 1
        keywords = ['fix', 'patch', 'logic', 'config', 'prompt', 'llm', 'security', 'doc']
        return sum(1 for kw in keywords if kw in text.lower())

    df['action_dispersity'] = df['title'].apply(count_actions)
    
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data=df, x='action_dispersity', hue='project_type', fill=True, common_norm=False)
    plt.title('Governance Action Dispersity Distribution', fontsize=14)
    plt.xlabel('Diversity of Remediation Actions')
    plt.savefig('output/metric_2_dispersity.png')

    # --- 指标 3: 信息填充率 (Information Density) ---
    # 检查核心字段是否为空
    fields_to_check = ['body', 'title', 'created_at', 'merged_at']
    df['info_density'] = df[fields_to_check].notna().mean(axis=1)
    
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='project_type', y='info_density', hue='project_type', palette='Set3', legend=False)
    plt.title('Governance Information Density Score', fontsize=14)
    plt.ylabel('Density Score (Completeness of PR Metadata)')
    plt.savefig('output/metric_3_density.png')
    
    print("分析完成！三张支撑指标图已保存至 output/ 文件夹。")

if __name__ == "__main__":
    if not os.path.exists('output'): os.makedirs('output')
    # 指向你爬取的 3000 条 JSON 文件
    json_file = 'medical_ai_full_data.json'
    if os.path.exists(json_file):
        generate_hard_metrics_plots(json_file)
    else:
        print(f"错误：找不到 {json_file}，请先运行爬虫脚本。")