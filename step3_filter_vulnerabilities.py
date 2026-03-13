import pandas as pd
import os

# 1. 定义真正关心的“漏洞/安全”关键词
SECURITY_KEYWORDS = [
    'vulnerability', 'exploit', 'security', 'cve', 'leak', 
    'attack', 'injection', 'unauthorized', 'privacy', 'hipaa',
    'medical data', 'breach', 'unsafe', 'poisoning', 'jailbreak'
]

# 2. 定义排除词（过滤掉广告、爬虫工具等噪音）
EXCLUDE_KEYWORDS = ['crawler', 'scrape', 'advertisement', '猫头鹰', '订阅']

def filter_data():
    input_file = "data/raw_data/all_medical_ai_bugs.csv"
    output_file = "data/refined_vulnerabilities.csv"
    
    if not os.path.exists(input_file):
        print("错误：找不到原始数据文件，请先运行 step2。")
        return

    # 读取数据
    df = pd.read_csv(input_file)
    print(f"原始数据共: {len(df)} 条")

    # 转换所有文本为小写以便匹配
    df['text_to_search'] = (df['title'].fillna('') + " " + df['body'].fillna('')).str.lower()

    # 过滤逻辑：
    # A. 必须包含安全关键词
    # B. 不能包含排除词
    # C. 或者 Labels 标签里本来就带有 bug 或 security
    
    condition_security = df['text_to_search'].apply(lambda x: any(k in x for k in SECURITY_KEYWORDS))
    condition_exclude = df['text_to_search'].apply(lambda x: any(k in x for k in EXCLUDE_KEYWORDS))
    condition_label = df['labels'].apply(lambda x: any(k in str(x).lower() for k in ['bug', 'security', 'critical']))

    refined_df = df[(condition_security | condition_label) & ~condition_exclude].copy()

    # 删除辅助列并保存
    refined_df.drop(columns=['text_to_search'], inplace=True)
    refined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"过滤完成！剩余精准信息: {len(refined_df)} 条")
    print(f"结果已保存至: {output_file}")

if __name__ == "__main__":
    filter_data()