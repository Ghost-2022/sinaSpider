#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
    date: 2021/10/25 18:42
    author: Ghost
    desc: 
"""
import sys

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from sina.spiders import sina_spider, sina_1


def start(key_word, start_time, end_time, search_id, token):

    process = CrawlerProcess(get_project_settings())

    process.crawl(sina_1.SinaSpider, key_word=key_word, start_time=start_time, end_time=end_time,
                  search_id=search_id, token=token)
    process.start()  # the script will block here until the crawling is finished


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 5:
        key_word = args[1]
        start_time = args[2]
        end_time = args[3]
        search_id = args[4]
        token = args[5]
        start(key_word, int(start_time), int(end_time), search_id, token)

