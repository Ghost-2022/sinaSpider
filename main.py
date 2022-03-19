#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/25 18:42
    author: Ghost
    desc: 
"""
import sys
import os
import redis
import json

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from sina.spiders import sina_spider, sina_1
from sina import settings


def start():
    conn = redis.Redis(
        host=settings.REDIS_SETTING['HOST'],
        port=settings.REDIS_SETTING['PORT'],
        password=settings.REDIS_SETTING['PASSWORD']
    )
    # data = json.loads(conn.rpoplpush('start_urls', 'start_urls'))
    data = conn.lpop('start_urls')
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'sina.settings'
    if data:
        data = json.loads(data)
        start_time = data['start_time']
        end_time = data['end_time']
        key_word = data['keyword']
        search_id = data['search_id']
        token = conn.get('sina-token').decode()

        process = CrawlerProcess(get_project_settings())

        process.crawl(sina_spider.SinaSpiderSpider, key_word=key_word, start_time=start_time, end_time=end_time,
                      search_id=search_id, token=token)
        process.start()  # the script will block here until the crawling is finished


if __name__ == '__main__':
    # args = sys.argv
    # if len(args) > 5:
    #     key_word = args[1]
    #     start_time = args[2]
    #     end_time = args[3]
    #     search_id = args[4]
    #     token = args[5]
    start()

