import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

# 读取 Excel 文件
excel_file = pd.ExcelFile('6.8热搜_高考英语.xlsx')

# 获取指定工作表中的数据
df = excel_file.parse('Sheet1')

# 提取评论列的数据，并去除缺失值后合并成一个字符串
text = ' '.join(df['评论'].dropna())

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300

# 设置中文字体为 SimHei
plt.rcParams['font.sans-serif'] = ['SimHei']

# 创建词云对象，使用 SimHei 字体路径
wordcloud = WordCloud(
    font_path='C:\Windows\Fonts\simhei.ttf',
    background_color='white',
    width=800,
    height=600
).generate(text)

# 显示词云
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
# 保存图片到数据可视化文件夹
image_path = os.path.join('数据可视化', '词云-6.8热搜_高考英语.png')
plt.savefig(image_path)

plt.show()