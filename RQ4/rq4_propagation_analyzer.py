import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os

def generate_refined_rq4_report(json_path):
    output_dir = 'output'
    if not os.path.exists(output_dir): os.makedirs(output_dir)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # --- 细化风险面探测逻辑 ---
    def detect_fine_grained_risks(row):
        text = (str(row.get('title', '')) + str(row.get('body', ''))).lower()
        return pd.Series({
            'API_Interoperability': any(k in text for k in ['api', 'webhook', 'request', 'integration']),
            'Log_Semantic_Leak': any(k in text for k in ['log', 'stdout', 'console', 'debug', 'trace']),
            'Export_Backup_Spread': any(k in text for k in ['export', 'backup', 'download', 'csv', 'dicom']),
            'Third_Party_Cloud': any(k in text for k in ['cloud', 'aws', 'azure', 'openai', 'external'])
        })

    risk_df = df.apply(detect_fine_grained_risks, axis=1)
    df = pd.concat([df, risk_df], axis=1)

    # 计算各类型的风险占比
    comparison = df.groupby('project_type')[risk_df.columns].mean() * 100
    comparison = comparison.reset_index().melt(id_vars='project_type', var_name='Risk_Dimension', value_name='Prevalence_Percentage')

    # --- 绘图：多维度风险面对比 ---
    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    
    ax = sns.barplot(data=comparison, x='Risk_Dimension', y='Prevalence_Percentage', hue='project_type', palette="viridis")
    
    plt.title('RQ4: Multi-Dimensional PHI Propagation Risk Profile', fontsize=14)
    plt.ylabel('Percentage of Cases with Risk Indicator (%)')
    plt.xticks(rotation=15)
    
    # 添加数值标注，增加细致感
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.1f}%', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', fontsize=10, color='black', xytext=(0, 5),
                    textcoords='offset points')

    save_path = os.path.join(output_dir, 'rq4_detailed_risk_profile.png')
    plt.savefig(save_path)
    print(f"细化分析完成！新图表已保存至: {save_path}")

if __name__ == "__main__":
    generate_refined_rq4_report('rq4_raw_leakage_data.json')