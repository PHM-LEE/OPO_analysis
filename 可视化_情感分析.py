import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 读取文件
df = pd.read_excel('6.8热搜合并后的文件_情感分析.xlsx')

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300

# 设置中文字体为 SimHei
plt.rcParams['font.sans-serif'] = ['SimHei']

# 创建一个 1 行 3 列的子图布局
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 绘制情感得分的直方图
sns.histplot(df['情感得分'], bins=20, kde=False, ax=axes[0])
axes[0].set_title('情感得分直方图')
axes[0].set_xlabel('情感得分')
axes[0].set_ylabel('频数')

# 绘制情感得分的箱线图
sns.boxplot(data=df['情感得分'], ax=axes[1])
axes[1].set_title('情感得分箱线图')
axes[1].set_xlabel('')
axes[1].set_ylabel('情感得分')

# 绘制情感得分的核密度图
sns.kdeplot(df['情感得分'], ax=axes[2])
axes[2].set_title('情感得分核密度图')
axes[2].set_xlabel('情感得分')
axes[2].set_ylabel('密度')

# 自动调整子图布局
plt.tight_layout()

# 创建数据可视化文件夹（如果不存在）
if not os.path.exists('数据可视化'):
    os.makedirs('数据可视化')

# 保存图片到数据可视化文件夹
image_path = os.path.join('数据可视化', '可视化-情感分析.png')
plt.savefig(image_path)

# 显示图形
plt.show()