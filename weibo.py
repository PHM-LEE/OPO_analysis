import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from openpyxl import Workbook
from openpyxl.styles import Font

cookies = {
    'SUB': '2A25FPrY7DeRhGeFG7lYS-SzLwjWIHXVmNbfzrDV6PUJbktAYLU7bkW1NeVi7r4VnATSLSpzI5EgN9Ijl-P8DoX77',
    'SUBP': '0033WrSXqPxfM725Ws9jqgMF55529P9D9WWd7J-e5WCDQTefKfv_PaHj5JpX5KMhUgL.FoMRSKB01KzN1K.2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMN1h-Xe0.ES0.4',
}

headers = {
    'authority': 'weibo.cn',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'max-age=0',
    'referer': 'https://weibo.cn/7854392799/info',
    'sec-ch-ua': '"Chromium";v="136", "Microsoft Edge";v="136", "Not.A/Brand";v="99"',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0',
}


def extract_weibo_id(url):
    """从微博URL中提取ID"""
    if not url:
        print('该微博没有URL,跳过')
        return ''

    # 尝试从多种URL格式中提取ID
    patterns = [
        r'weibo\.com/(\d+)/\w+',
        r'weibo\.com/\w+/(\w+)',
        r'status/(\w+)',
        r'/(\w{9})(?:\?|$)',
        r'q=([a-zA-Z0-9%]+)',
        r'topic/(\d+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ''

# 获取当前日期时间
current_time = datetime.now().strftime("%Y%m%d%H%M")

# 发送 HTTP 请求获取微博热搜页面
response = requests.get('https://s.weibo.com/top/summary', cookies=cookies, headers=headers)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# 存储热搜数据的列表
hot_data = []

# 获取热搜列表（包括置顶的广告）
hot_items = soup.select('#pl_top_realtimehot > table > tbody > tr')[:51]  # 前50个热搜+置顶

for item in hot_items:
    try:
        # 排名
        rank_elem = item.select_one('td.ranktop')
        rank = rank_elem.text.strip() if rank_elem else '置顶'

        # 标题和链接
        title_elem = item.select_one('td.td-02 a')
        title = title_elem.text.strip() if title_elem else '未知'
        href = title_elem.get('href') if title_elem else ''
        full_url = f"https://s.weibo.com{href}" if href.startswith('/') else href

        # 提取ID
        weibo_id = extract_weibo_id(full_url)

        # 热度值
        hot_value_elem = item.select_one('td.td-02 span')
        hot_value = hot_value_elem.text.strip() if hot_value_elem else '未知'

        # 热度类型（如：沸、热、新等）
        hot_type_elem = item.select_one('td.td-03 i')
        hot_type = hot_type_elem.text.strip() if hot_type_elem else ''

        hot_data.append({
            '日期时间': current_time,
            '排名': rank,
            '标题': title,
            '热度值': hot_value,
            '热度类型': hot_type,
            '链接': full_url,
            'ID': weibo_id
        })

    except Exception as e:
        print(f"解析单个热搜项时出错: {e}")
        continue

os.makedirs("weibohot", exist_ok=True)

# 创建工作簿和工作表
wb = Workbook()
ws = wb.active
ws.title = "微博热搜"

# 添加标题行并设置字体为粗体
headers = ["ID", "日期时间", "排名", "标题", "热度值", "热度类型", "链接"]
ws.append(headers)
for cell in ws[1]:
    cell.font = Font(bold=True)

# 写入数据
for data in hot_data:
    row = [
        data['ID'],
        data['日期时间'],
        data['排名'],
        data['标题'],
        data['热度值'],
        data['热度类型'],
        data['链接']
    ]
    ws.append(row)

# 调整列宽以适应内容
for column_cells in ws.columns:
    length = max(len(str(cell.value)) for cell in column_cells)
    ws.column_dimensions[column_cells[0].column_letter].width = length * 1.2

# 数据存储
output_file = f"weibo_hotsearch_{current_time}.xlsx"
wb.save(output_file)

print(f"已成功爬取 {len(hot_data)} 条热搜数据并保存至 {output_file}")