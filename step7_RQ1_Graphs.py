import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 初始化设置
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
sns.set_context("paper", font_scale=1.2)

# 加载数据
df = pd.read_csv("data/RQ1_final_landscape.csv")
df['date'] = pd.to_datetime(df['date'])

# --- 1. 修复 CWE 分布图 (增加高度，自动防止标签截断) ---
plt.figure(figsize=(14, 10)) # 增加高度
cwe_order = df['cwe'].value_counts().index
sns.countplot(data=df, y='cwe', order=cwe_order, palette="magma")

plt.title('Top CWE 缺陷类别分布 (全量统计)', fontsize=16, pad=20)
plt.xlabel('发现频次', fontsize=12)
plt.ylabel('CWE 编号及描述', fontsize=12)

# 核心修复：自动调整子图参数，使之填充整个图像区域
plt.tight_layout() 
plt.savefig('data/RQ1_CWE_Bar_Fixed.png', dpi=300) # 提高分辨率
print("CWE 分布图已重新生成：data/RQ1_CWE_Bar_Fixed.png")

# --- 2. 修复 演化热力图 (调整边距，确保文字完整) ---
plt.figure(figsize=(15, 9)) # 增加宽度以适应年份
heatmap_data = pd.crosstab(df['cwe'], df['year'])

# 使用 seaborn 的 heatmap 并显式调整 cbar（侧边条）位置，防止挤压
sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="YlGnBu", 
            cbar_kws={'label': '漏洞数量'}, linewidths=.5)

plt.title('缺陷类型随时间的演化分布热力图 (2020-2026)', fontsize=16, pad=20)
plt.xlabel('年份', fontsize=12)
plt.ylabel('CWE 类别', fontsize=12)

# 核心修复：旋转 Y 轴标签防止重叠，并留出足够的左边距
plt.yticks(rotation=0)
plt.tight_layout() 
plt.savefig('data/RQ1_Heatmap_Evolution_Fixed.png', dpi=300)
print("演化热力图已重新生成：data/RQ1_Heatmap_Evolution_Fixed.png")