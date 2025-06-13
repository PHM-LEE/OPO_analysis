import pandas as pd
import matplotlib.pyplot as plt
import jieba
from wordcloud import WordCloud
from snownlp import SnowNLP
from collections import Counter
import re
from datetime import datetime
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 设置中文字体
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]

# 创建必要的目录
os.makedirs("weibohot_worldcloud", exist_ok=True)
os.makedirs("weibohot_sentiment_analysis", exist_ok=True)
os.makedirs("sentiment_results", exist_ok=True)


def get_current_time():
    """获取当前时间字符串，格式为YYYYMMDDHHMMSS"""
    return datetime.now().strftime("%Y%m%d%H%M%S")


def read_hotsearch_data(file_path):
    """读取微博热搜数据"""
    try:
        # 尝试读取CSV格式
        df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='warn')

        # 检查列名并尝试自动识别
        column_mapping = {
            'title': '标题',
            'content': '标题',
            'name': '标题',
            '热搜': '标题',
            '话题': '标题',
            'rank': '排名',
            'hot': '热度值',
            'score': '热度值',
            'type': '热度类型',
            'category': '热度类型'
        }

        # 重命名列
        df = df.rename(columns=lambda x: column_mapping.get(x.lower(), x))

        # 确保有标题列
        if '标题' not in df.columns:
            # 尝试通过内容推断标题列
            for col in df.columns:
                if df[col].dtype == 'object' and len(df[col].str.split()) > 0:
                    df = df.rename(columns={col: '标题'})
                    break

        if '标题' not in df.columns:
            raise ValueError("无法识别标题列，请检查数据格式")

        return df

    except Exception as e:
        logger.error(f"读取CSV失败: {e}")
        try:
            # 尝试读取Excel格式
            df = pd.read_excel(file_path)
            return df
        except:
            logger.error("也未能读取Excel格式")

        # 尝试读取txt格式
        try:
            data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        # 尝试多种分隔符
                        parts = re.split(r'[,|\t]', line)
                        if len(parts) >= 3:  # 至少有排名、标题、热度
                            data.append({
                                '排名': parts[0],
                                '标题': parts[1],
                                '热度值': parts[2] if len(parts) > 2 else '',
                                '热度类型': parts[3] if len(parts) > 3 else ''
                            })
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"读取TXT失败: {e}")
            return pd.DataFrame()


def clean_text(text):
    """清理文本"""
    if not isinstance(text, str):
        return ""

    # 去除URL
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # 去除特殊字符和标点
    text = re.sub(r'[^\w\s]', '', text)
    # 去除空格和换行
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def generate_wordcloud(text_data, output_path=None):
    """生成词云"""
    if not text_data:
        logger.warning("没有可用的文本数据生成词云")
        return None

    if output_path is None:
        current_time = get_current_time()
        output_path = f"weibohot_worldcloud/{current_time}_wordcloud.png"

    try:
        # 合并所有标题文本
        all_text = ' '.join([clean_text(t) for t in text_data if clean_text(t)])

        # 使用jieba进行中文分词
        words = jieba.lcut(all_text)

        # 扩展停用词列表
        stopwords = set([
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到',
            '说',
            '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这', '那', '这个', '那个', '啊', '吧', '把',
            '被',
            '热搜', '微博', '话题', '更多', '视频', '搜索', '查看', '点击', '网页', '链接', '正在'
        ])

        # 过滤停用词并统计词频
        word_freq = Counter()
        for word in words:
            word = word.strip()
            if word and word not in stopwords and len(word) > 1:  # 过滤单个字符
                word_freq[word] += 1

        if not word_freq:
            logger.warning("没有有效的词汇生成词云")
            return None

        # 生成词云
        wordcloud = WordCloud(
            font_path='simhei.ttf',
            width=1200,
            height=600,
            background_color='white',
            max_words=200,
            collocations=False,  # 避免重复词语
            scale=2  # 提高清晰度
        ).generate_from_frequencies(word_freq)

        # 保存词云图
        wordcloud.to_file(output_path)

        # 显示词云图
        plt.figure(figsize=(12, 8))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('微博热搜词云', fontsize=16)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', quality=95)
        plt.close()

        logger.info(f"词云已保存至 {output_path}")
        return word_freq

    except Exception as e:
        logger.error(f"生成词云时出错: {e}")
        return None


def contains_negative_words(text):
    """检查是否包含负面词汇"""
    negative_words = [
        '不', '没有', '未', '无', '拒绝', '反对', '抗议', '谴责', '批评', '指责',
        '失望', '愤怒', '伤心', '难过', '痛苦', '悲剧', '灾难', '死亡', '事故', '失败',
        '问题', '困难', '挑战', '危机', '冲突', '战争', '暴力', '犯罪', '诈骗', '欺骗'
    ]
    return any(word in text for word in negative_words)


def contains_positive_words(text):
    """检查是否包含正面词汇"""
    positive_words = [
        '好', '优秀', '成功', '胜利', '开心', '快乐', '幸福', '喜悦', '满意', '赞成',
        '支持', '庆祝', '成就', '进步', '发展', '创新', '突破', '冠军', '奖励', '荣誉',
        '爱', '喜欢', '感谢', '感激', '美好', '漂亮', '精彩', '完美', '优秀', '强大'
    ]
    return any(word in text for word in positive_words)


def analyze_sentiment(text):
    """综合情感分析"""
    text = clean_text(text)
    if not text:
        return None, 0.5  # 中性默认值

    # 使用SnowNLP获取基础情感分数
    try:
        s = SnowNLP(text)
        base_score = s.sentiments
    except:
        base_score = 0.5

    # 调整分数基于关键词
    if contains_negative_words(text):
        adjusted_score = base_score * 0.7  # 降低分数
    elif contains_positive_words(text):
        adjusted_score = base_score * 1.3  # 提高分数
    else:
        adjusted_score = base_score

    # 确保分数在0-1之间
    adjusted_score = max(0, min(1, adjusted_score))

    # 最终分类
    if adjusted_score > 0.7:
        return "positive", adjusted_score
    elif adjusted_score < 0.3:
        return "negative", adjusted_score
    else:
        return "neutral", adjusted_score


def sentiment_analysis(text_data, output_prefix=None):
    """情感分析并生成可视化结果和文本文件"""
    if not text_data:
        logger.warning("没有可用的文本数据进行情感分析")
        return None

    if output_prefix is None:
        current_time = get_current_time()
        output_prefix = f"weibohot_sentiment_analysis/{current_time}_sentiment"

    try:
        # 初始化结果
        results = {
            'positive': {'count': 0, 'examples': []},
            'neutral': {'count': 0, 'examples': []},
            'negative': {'count': 0, 'examples': []},
            'total': 0
        }

        for text in text_data:
            sentiment, score = analyze_sentiment(text)
            if sentiment is None:
                continue

            results[sentiment]['count'] += 1
            results[sentiment]['examples'].append((text, score))
            results['total'] += 1

        if results['total'] == 0:
            logger.warning("没有有效的情感分析结果")
            return None

        # 计算比例
        results['positive']['percent'] = results['positive']['count'] / results['total'] * 100
        results['neutral']['percent'] = results['neutral']['count'] / results['total'] * 100
        results['negative']['percent'] = results['negative']['count'] / results['total'] * 100

        # 绘制柱状图
        image_path = f"{output_prefix}.png"
        plt.figure(figsize=(12, 8))

        labels = ['正面', '中立', '负面']
        counts = [results['positive']['count'], results['neutral']['count'], results['negative']['count']]
        percentages = [results['positive']['percent'], results['neutral']['percent'], results['negative']['percent']]

        bars = plt.bar(labels, counts, color=['#4CAF50', '#2196F3', '#F44336'], width=0.6)

        # 添加数据标签
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{counts[i]}条 ({percentages[i]:.1f}%)',
                     ha='center', va='bottom', fontsize=12)

        plt.title('微博热搜情感分析结果', fontsize=16)
        plt.xlabel('情感类别', fontsize=14)
        plt.ylabel('数量', fontsize=14)
        plt.xticks(fontsize=12)
        plt.yticks(fontsize=12)
        plt.tight_layout()
        plt.savefig(image_path, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"情感分析柱状图已保存至 {image_path}")

        # 保存所有情感分析结果到一个文本文件
        text_output_path = f"sentiment_results/{os.path.basename(output_prefix)}_results.txt"
        with open(text_output_path, 'w', encoding='utf-8') as f:
            # 写入汇总信息
            f.write("=== 微博热搜情感分析结果 ===\n\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总条目数: {results['total']}\n\n")

            f.write("=== 分类统计 ===\n")
            f.write(f"正面情绪: {results['positive']['count']}条 ({results['positive']['percent']:.1f}%)\n")
            f.write(f"中立情绪: {results['neutral']['count']}条 ({results['neutral']['percent']:.1f}%)\n")
            f.write(f"负面情绪: {results['negative']['count']}条 ({results['negative']['percent']:.1f}%)\n\n")

            # 写入正面情绪示例
            f.write("\n=== 正面情绪示例 ===\n")
            for i, (text, score) in enumerate(
                    sorted(results['positive']['examples'], key=lambda x: x[1], reverse=True)[:20]):
                f.write(f"{i + 1}. [{score:.3f}] {text}\n")

            # 写入负面情绪示例
            f.write("\n=== 负面情绪示例 ===\n")
            for i, (text, score) in enumerate(sorted(results['negative']['examples'], key=lambda x: x[1])[:20]):
                f.write(f"{i + 1}. [{score:.3f}] {text}\n")

            # 写入中立情绪示例
            f.write("\n=== 中立情绪示例 ===\n")
            for i, (text, score) in enumerate(results['neutral']['examples'][:20]):
                f.write(f"{i + 1}. [{score:.3f}] {text}\n")

        logger.info(f"情感分析结果已保存至 {text_output_path}")

        return results

    except Exception as e:
        logger.error(f"情感分析时出错: {e}")
        return None


def main():
    """主函数"""
    # 文件路径
    input_file = 'weibohot/weibo_hotsearch_202506011411.csv'  # 请替换为实际文件路径

    # 读取数据
    logger.info(f"开始读取数据文件: {input_file}")
    df = read_hotsearch_data(input_file)

    if df.empty:
        logger.error("未找到数据或数据格式错误")
        return

    logger.info(f"成功读取 {len(df)} 条热搜数据")
    logger.info("数据样例:\n" + str(df.head(3)))

    # 提取标题列
    titles = df['标题'].dropna().tolist()

    # 生成词云
    logger.info("开始生成词云...")
    word_freq = generate_wordcloud(titles)

    if word_freq:
        # 打印高频词
        logger.info("\n高频词统计:")
        for word, count in word_freq.most_common(20):
            logger.info(f"{word}: {count}次")

    # 情感分析
    logger.info("开始情感分析...")
    sentiment_result = sentiment_analysis(titles)

    if sentiment_result:
        # 打印情感分析结果
        logger.info("\n情感分析结果:")
        logger.info(f"正面: {sentiment_result['positive']['count']}条 ({sentiment_result['positive']['percent']:.1f}%)")
        logger.info(f"中立: {sentiment_result['neutral']['count']}条 ({sentiment_result['neutral']['percent']:.1f}%)")
        logger.info(f"负面: {sentiment_result['negative']['count']}条 ({sentiment_result['negative']['percent']:.1f}%)")


if __name__ == "__main__":
    main()