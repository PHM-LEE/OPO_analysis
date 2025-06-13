import re
import requests
import pandas as pd

# 请求头（包含Cookie）
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36',
    'Cookie': 'CF=AolsrwT1dn39lJ99mLPWsQoPrd812jxYmCgrDZsGqVP8ABrLWyiO3ruQtUc3ygo2GAzKT9ZfJk9-_5k8ywsbEbY.; SUB=_2A25FPrY7DeRhGeFG7lYS-SzLwjWIHXVmNbfzrDV6PUJbktAYLU7bkW1NeVi7r4VnATSLSpzI5EgN9Ijl-P8DoX77; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWd7J-e5WCDQTefKfv_PaHj5JpX5KMhUgL.FoMRSKB01KzN1K.2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMN1h-Xe0.ES0.4; ALF=1751274347; _T_WM=1febb1701202980d8f91c10767cc6d25; MLOGIN=1; WEIBOCN_FROM=1110006030; XSRF-TOKEN=cff8a8; mweibo_short_token=e4d31661af; M_WEIBOCN_PARAMS=oid%3D5173492790331183%26lfid%3D231583%26luicode%3D20000174%26uicode%3D10000011%26fid%3D102803'
}
url = 'https://m.weibo.cn/comments/hotflow?id=5172818595549488&mid=5172818595549488&max_id_type=0'

try:
    # 发送请求并解析JSON
    response = requests.get(url=url, headers=headers)
    response.raise_for_status()  # 检查请求是否成功

    # 存储所有评论数据的列表
    comments_list = []

    # 遍历每条评论
    for comment in response.json()['data']['data']:
        # 获取用户信息
        user = comment['user']

        # 提取纯中文评论内容
        content = ''.join(re.findall('[\u4e00-\u9fa5]+', comment['text']))

        # 转换性别代码为中文
        gender = '女' if user.get('gender') == 'f' else '男' if user.get('gender') == 'm' else '未知'

        # 构建完整的评论信息字典
        comment_data = {
            '用户': user.get('screen_name', '未知用户'),
            '性别': gender,
            'svip': user.get('svip', 0),  # 0表示非SVIP，1表示SVIP
            '地区': comment.get('source', '').replace('来自', '').strip() or '未知',
            '评论': content,
            '日期': comment.get('created_at', '未知日期')
        }

        comments_list.append(comment_data)
        print(f"用户: {comment_data['用户']} | 性别: {gender} | 评论: {content[:30]}...")

    # 保存到Excel
    if comments_list:
        pd_data = pd.DataFrame(comments_list)
        pd_data.to_excel('微博评论_完整版.xlsx', index=False)
        print(f"成功保存{len(comments_list)}条评论数据到Excel")
    else:
        print("未获取到评论数据")

except requests.exceptions.RequestException as e:
    print(f"请求出错: {e}")
except (KeyError, ValueError) as e:
    print(f"数据解析错误: {e}")
    print("响应内容预览:", response.text[:300])
except Exception as e:
    print(f"未知错误: {e}")