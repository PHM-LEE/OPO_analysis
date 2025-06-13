
import pandas as pd
import matplotlib.pyplot as plt
import os

# 设置中文字体为 SimHei
plt.rcParams['font.sans-serif'] = ['SimHei']
# 用来正常显示负号
plt.rcParams['axes.unicode_minus'] = False

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300

# 读取 Excel 文件
excel_file = pd.ExcelFile('6.8热搜_高考英语.xlsx')

# 获取指定工作表中的数据
df = excel_file.parse('Sheet1')

# 创建一个包含 1 行 3 列的子图布局
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# 绘制性别分布饼图
gender_distribution = df['性别'].value_counts()
axes[0].pie(gender_distribution, labels=gender_distribution.index, autopct='%1.1f%%')
axes[0].set_title('性别分布')

# 绘制 svip 数量柱状图
svip_counts = df['svip'].value_counts()
axes[1].bar(svip_counts.index.astype(str), svip_counts)
axes[1].set_xlabel('svip')
axes[1].set_ylabel('数量')
axes[1].set_title('svip 数量分布')

# 绘制不同地区的用户数柱状图
region_counts = df['地区'].value_counts()
axes[2].bar(region_counts.index, region_counts)
axes[2].set_xlabel('地区')
axes[2].set_ylabel('用户数')
axes[2].set_title('不同地区的用户数分布')

# 设置 x 轴标签旋转 90 度
axes[2].tick_params(axis='x', rotation=90)

# 自动调整子图布局
plt.tight_layout()

# 创建数据可视化文件夹（如果不存在）
if not os.path.exists('数据可视化'):
    os.makedirs('数据可视化')

# 保存图片到数据可视化文件夹
image_path = os.path.join('数据可视化', '6.8热搜_高考英语.png')
plt.savefig(image_path)

# 显示图形（可选，如果在非交互式环境下运行，这一步可以省略）
plt.show()