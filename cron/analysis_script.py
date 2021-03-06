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
import traceback

import jieba
import collections
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from snownlp import SnowNLP

from sina import database, settings
conn_pool = database.get_conn()
cursor, conn = conn_pool.get_conn()

article_table = 'article_list'
comment_table = 'comment_list'


def get_content_list(search_id, table='article_list'):
    """
    获取文本数据
    :param search_id:
    :param table:
    :return:
    """
    sql = f"select content from {table} where search_id = {search_id}"
    cursor.execute(sql)
    return [re.sub('[^\u4e00-\u9fa5]', '', item[0],) for item in cursor.fetchall()]


def generate_word_cloud(content_list, search_id, table):
    if not content_list:
        return {}
    content = re.sub('\[.*?\]|http[:/\.\w]*|\s', '', ' '.join(content_list))
    space_list = [item for item in jieba.lcut(content) if len(item) >= 2]
    counts = collections.Counter(space_list)
    # logging.info(f'space_list: {counts}')
    font_path = os.path.join(settings.PROJECT_PATH, 'cron/AaBanRuoKaiShu-2.ttf')
    wc = WordCloud(width=550, height=400,
                   background_color='white',
                   mode='RGB',
                   max_words=500,
                   stopwords=STOPWORDS.add('微博'),  # 内置的屏蔽词,并添加自己设置的词语
                   font_path=font_path,
                   max_font_size=150,
                   relative_scaling=0.6,  # 设置字体大小与词频的关联程度为0.4
                   random_state=50,
                   collocations=False,
                   scale=2
                   ).generate_from_frequencies(counts)
    img_name = table.split('_')[0]+'.jpg'
    img_dir = os.path.join(settings.STATIC_DIR, f'search_{search_id}')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)
    img_abs_path = os.path.join(img_dir, img_name)
    wc.to_file(img_abs_path)  # 保存词云图
    return counts


def emotion_analysis(content_list):
    """
    情感分析，分析每条文章和评论的感情信息

    :param content_list: 文章列表
    :return:
    """
    negative, positive, neutral = 0, 0, 0
    for item in content_list:
        if item:
            s = SnowNLP(item)
        else:
            # logging.error(f'内容：{item}情感分析失败：{traceback.format_exc()}')
            continue
        if s.sentiments >= 0.6:
            positive += 1
        elif s.sentiments >= 0.4:
            neutral += 1
        else:
            negative += 1
    data = [
        {'name': '积极', 'value': positive},
        {'name': '消极', 'value': negative},
        {'name': '中性', 'value': neutral},
    ]
    return data


def group_statistics(content_list):
    """
    分类统计

    :return:
    """
    sql = "select label, rule from label_list WHERE is_del=0 limit 10;"
    cursor.execute(sql)
    rule_list = cursor.fetchall()
    result = {'其他': 0}
    for content in content_list:
        flag = False
        for item in rule_list:
            if re.findall(item[1], content):
                if item[0] not in result:
                    result[item[0]] = 0
                flag = True
                result[item[0]] += 1
        if not flag:
            result['其他'] += 1
    data = [{'name': k, 'value': v} for k, v in result.items()]
    return data


def main(search_id):
    article_list = get_content_list(search_id, article_table)
    comment_list = get_content_list(search_id, comment_table)
    a_word_count = generate_word_cloud(article_list, search_id, article_table)
    c_word_count = generate_word_cloud(comment_list, search_id, comment_table)
    a_word_list = [{'name': item[0], 'value': item[1]} for item in
                   sorted(a_word_count.items(), key=lambda kv:(kv[1], kv[0]),
                          reverse=True)[:20]]
    c_word_list = [{'name': item[0], 'value': item[1]} for item in
                   sorted(c_word_count.items(), key=lambda kv: (kv[1], kv[0]),
                          reverse=True)[:20]]
    article_emotion = emotion_analysis(article_list)
    comment_emotion = emotion_analysis(comment_list)
    a_group_count = group_statistics(article_list)
    c_group_count = group_statistics(comment_list)

    data = {
        'comment_counts': c_word_list,
        'article_counts': a_word_list,
        'article_emotion': article_emotion,
        'comment_emotion': comment_emotion,
        'a_group_count': a_group_count,
        'c_group_count': c_group_count
    }
    return data


if __name__ == '__main__':
    # print(get_data(20))
    # generate_word_cloud(7, 'article_list')
    # generate_word_cloud(20, 'comment_list')
    # emotion_analysis(20, 'article_list')
    # emotion_analysis(20, 'comment_list')
    # print(group_statistics(7, 'article_list'))
    main(29)
