import pandas as pd
import os
from snownlp import SnowNLP

# 获取当前目录
file_dir = os.getcwd()

# 获取指定目录下的所有文件
file_names = os.listdir(file_dir)

# 用于存储数据的列表
dfs = []

# 遍历文件列表
for file_name in file_names:
    # 检查文件是否为 Excel 文件（支持.xlsx 和.xls 格式）
    if file_name.endswith(('.xlsx', '.xls')):
        file_path = os.path.join(file_dir, file_name)
        try:
            # 读取 Excel 文件
            excel_file = pd.ExcelFile(file_path)
            # 获取所有表名
            sheet_names = excel_file.sheet_names
            for sheet_name in sheet_names:
                # 获取指定工作表中的数据
                df = excel_file.parse(sheet_name)
                # 将数据添加到列表中
                dfs.append(df)
        except Exception as e:
            print(f'读取文件 {file_name} 时出现错误: {e}')

# 合并所有数据
combined_df = pd.concat(dfs, ignore_index=True)

# 假设评论列名为'评价'，对评论进行情感分析，并将结果保留两位小数
if '标题' in combined_df.columns:
    combined_df['情感得分'] = combined_df['标题'].apply(lambda x: round(SnowNLP(str(x)).sentiments, 2))
else:
    print("数据中不存在'标题'列，无法进行情感分析。")

# 将合并后的数据保存为新的 Excel 文件
output_file_path = '6.8热搜合并后的文件_情感分析.xlsx'
combined_df.to_excel(output_file_path, index=False)