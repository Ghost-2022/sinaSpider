#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/29 19:12
    author: Ghost
    desc: 
"""
import logging
import re
import os

import jieba
import collections
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from snownlp import SnowNLP

from sina import database, settings
conn_pool = database.get_conn()
cursor, conn = conn_pool.get_conn()


def get_article_data(search_id, table='article_list'):
    sql = f"select content from {table} where search_id = {search_id}"
    cursor.execute(sql)
    return [item[0].decode() for item in cursor.fetchall()]


def get_data(search_id, table='article_list'):
    content_list = get_article_data(search_id, table)
    content = re.sub('\[.*?\]|http[:/\.\w]*|\s', '', ' '.join(content_list))
    return [item for item in jieba.lcut(content) if len(item) >= 2]


def generate_word_cloud(search_id, table):
    space_list = get_data(search_id, table)
    logging.info(f'space_list: {space_list}')
    counts = collections.Counter(space_list)
    font_path = os.path.join(settings.PROJECT_PATH, 'cron/AaBanRuoKaiShu-2.ttf')
    wc = WordCloud(width=1400, height=2200,
                   background_color='white',
                   mode='RGB',
                   # mask=back_ground,  # 添加蒙版，生成指定形状的词云，并且词云图的颜色可从蒙版里提取
                   max_words=500,
                   stopwords=STOPWORDS.add('微博'),  # 内置的屏蔽词,并添加自己设置的词语
                   font_path=font_path,
                   max_font_size=150,
                   relative_scaling=0.6,  # 设置字体大小与词频的关联程度为0.4
                   random_state=50,
                   scale=2
                   ).generate(' '.join(space_list))

    plt.imshow(wc)  # 显示词云
    plt.axis('off')  # 关闭x,y轴
    img_name = table.split('_')[0]+'.png'
    img_dir = os.path.join(settings.STATIC_DIR, f'search_{search_id}')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    img_abs_path = os.path.join(img_dir, img_name)
    wc.to_file(img_abs_path)  # 保存词云图
    # img_path = os.path.join(f'search_{search_id}', img_name)
    return counts


def emotion_analysis(search_id, table):
    content_list = get_article_data(search_id, table)
    data = {'negative': 0, 'positive': 0, 'neutral': 0}
    for item in content_list:
        s = SnowNLP(item)
        if s.sentiments >= 0.6:
            data['positive'] += 1
        elif s.sentiments >= 0.4:
            data['neutral'] += 1
        else:
            data['negative'] += 1
    return data


if __name__ == '__main__':
    # print(get_data(20))
    # generate_word_cloud(20, 'article_list')
    # generate_word_cloud(20, 'comment_list')
    emotion_analysis(20, 'article_list')
    emotion_analysis(20, 'comment_list')