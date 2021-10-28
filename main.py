#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/25 18:42
    author: Ghost
    desc: 
"""
import os
import redis
import json

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from sina.spiders import sina_spider


def start():
    conn = redis.Redis(host='146.56.219.98', port=16379, password='Qm1lrYiMe8wx2sT7')
    data = json.loads(conn.lrange('start_urls', 0, 10)[0])
    start_time = data['start_time']
    end_time = data['end_time']
    key_word = data['keyword']
    search_id = data['search_id']

    process = CrawlerProcess(get_project_settings())

    process.crawl(sina_spider.SinaSpiderSpider, key_word=key_word,
                  start_time=start_time, end_time=end_time, search_id=search_id)
    process.start()  # the script will block here until the crawling is finished


if __name__ == '__main__':
    # key = '疫情'
    # start_time = '2021-10-15-10'
    # end_time = '2021-10-16-14'
    # search_id = 20
    start()

