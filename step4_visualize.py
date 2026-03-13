import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 设置中文字体（如果是中文环境，防止乱码）
plt.rcParams['font.sans-serif'] = ['SimHei'] 
plt.rcParams['axes.unicode_minus'] = False

def create_visualizations():
    input_file = "data/raw_data/all_medical_ai_bugs.csv"
    if not os.path.exists(input_file):
        print("错误：未找到数据文件！")
        return

    df = pd.read_csv(input_file)
    
    # --- 1. 数据清洗：提取漏洞类别 ---
    # 我们定义几个医疗AI常见的关注维度
    categories = {
        'Security/Privacy': ['security', 'vulnerability', 'privacy', 'leak', 'hipaa', 'cve'],
        'Model Errors': ['accuracy', 'hallucination', 'wrong diagnosis', 'error', 'model'],
        'Data Issues': ['dataset', 'missing data', 'csv', 'image format', 'dicom'],
        'Agent Logic': ['agent', 'logic', 'workflow', 'planning', 'failed'],
        'Installation/Env': ['install', 'pip', 'environment', 'docker', 'build']
    }

    def classify(row):
        text = (str(row['title']) + " " + str(row['body'])).lower()
        for cat, keywords in categories.items():
            if any(k in text for k in keywords):
                return cat
        return 'General/Others'

    df['Category'] = df.apply(classify, axis=1)

    # --- 2. 绘图：类别分布饼图 ---
    plt.figure(figsize=(10, 7))
    category_counts = df['Category'].value_counts()
    plt.pie(category_counts, labels=category_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title('AI 医疗任务数据类别分布 (N=4079)')
    plt.savefig('data/category_distribution.png')
    print("图表1已生成：类别分布饼图")

    # --- 3. 绘图：各仓库贡献 Issues 数量 (Top 15) ---
    plt.figure(figsize=(12, 6))
    repo_counts = df['repo'].value_counts().head(15)
    sns.barplot(x=repo_counts.values, y=repo_counts.index, palette='viridis')
    plt.title('最活跃的医疗AI仓库 Top 15 (按问题数量)')
    plt.xlabel('Issues/PRs 数量')
    plt.savefig('data/top_repositories.png')
    print("图表2已生成：热门仓库柱状图")

    # --- 4. 绘图：时间分布趋势 ---
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['Month'] = df['created_at'].dt.to_period('M')
    trend_data = df.groupby('Month').size()
    
    plt.figure(figsize=(12, 6))
    trend_data.plot(kind='line', marker='o', color='red')
    plt.title('医疗 AI 漏洞/问题反馈随时间变化趋势')
    plt.ylabel('反馈数量')
    plt.grid(True)
    plt.savefig('data/time_trend.png')
    print("图表3已生成：时间趋势图")

if __name__ == "__main__":
    create_visualizations()