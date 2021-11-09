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
    return [item[0].decode() for item in cursor.fetchall()]


def generate_word_cloud(content_list, search_id, table):
    content = re.sub('\[.*?\]|http[:/\.\w]*|\s', '', ' '.join(content_list))
    space_list = [item for item in jieba.lcut(content) if len(item) >= 2]
    logging.info(f'space_list: {space_list}')
    counts = collections.Counter(space_list)
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
                   scale=2
                   ).generate(' '.join(space_list))
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
        s = SnowNLP(item)
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
    rule_list = [
        ('震情', '中国地震台网|北纬|东经|余震|三级以上|最大地震|地震快讯|震情周报|震中距|经度|纬度'),
        ('祈福', '平安|祈福|祈祷|希望|保佑|愿'),
        ('人员伤亡情况', '受伤|重伤|轻伤|死|亡'),
        ('震感', '晕|晃|摇|震感|感觉|又震了|又来了|坐标|抖|又开始了|跑|睡'),
        ('生命线工程情况', '铁路|高速|路况|封路|交通|信号|停电|停水|断网|列车|供电|高铁|道路|桥|电网'),
        ('房屋破坏', '房|屋|墙|楼|倒|塌|裂|掉|碎'),
        ('救援行动', '救援|奔赴|赶赴|物资|消防|应急避难|应急预案|续报|地震局|应急现场|地震应急|应急管理|救灾|安置'),
        ('地震科普', '科普|科学避震|知识|自救方法|专家|防范措施|谣言|躲避地震|学习|避险|预警|前兆|地震波'),
        ('心理变化', '害怕|恐怖|吓|不敢|呜呜|怕|幻觉|担心|怎么样|想问|求求|还好|淡定'),
        ('为应急响应点赞', '赞|点赞|棒棒|表扬|加油|挺住|相信|感动|厉害'),
    ]
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
    a_word_list = [{item[0]: item[1]} for item in
                   sorted(a_word_count.items(), key=lambda kv:(kv[1], kv[0]),
                          reverse=True)[:20]]
    c_word_list = [{item[0]: item[1]} for item in
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
    main(7)