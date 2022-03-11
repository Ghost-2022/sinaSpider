import time
import re
from urllib import parse
import json
import datetime

import scrapy
from scrapy import Request

from sina import settings, items, sina_utils

f_article = 'https://c.api.weibo.com/2/search/statuses/limited.json?access_token={}&q={}&starttime={}&endtime={' \
        '}&count=50&page={}'
f_comment = 'https://c.api.weibo.com/2/comments/show/all.json?access_token={}&id={}&count=100&page={}'


class SinaSpider(scrapy.Spider):
    name = 'sina'
    allowed_domains = ['weibo.com']

    def __init__(self, key_word=None, token=None, start_time: int = 0,
                 end_time: int = 0, search_id: int = 0, *args, **kwargs):
        super(SinaSpider, self).__init__(*args, **kwargs)
        self.logger.info(f'爬取关键字：{key_word}, {start_time}, {end_time}')
        self.start_time, self.end_time, self.key_word = start_time, end_time, key_word
        self.search_id, self.token = search_id, token
        self.start_urls = [f_article.format(token, key_word, start_time, end_time, 1)]

    def parse(self, response: scrapy.http.Response, **kwargs):
        try:
            data = json.loads(response.text)
        except Exception:
            self.logger.error(f'数据解析异常：{response.url}')
            return
        total = data.get('total_number', 0)
        if not data.get('statuses', []):
            return
        for i in range(2, 200):
            url = f_article.format(self.token, self.key_word, self.start_time, self.end_time, i)
            yield Request(url, callback=self.parse)
        for item in data.get('statuses', []):
            content_item = items.SinaItem()
            content_item['detail_id'] = item['id']
            user_id = item.get('user', {}).get('id')
            mid = sina_utils.id2mid(item['id'])
            content_item['author'] = item.get('user', {}).get('name')
            profile_url = item.get('user', {}).get('profile_url', '')
            content_item['author_url'] = parse.urljoin('https://weibo.com/', profile_url) if profile_url else ''
            try:
                pub_time = datetime.datetime.strptime(item.get('created_at', ''), '%a %b %d %H:%M:%S %z %Y')
            except Exception:
                pub_time = datetime.datetime.now()
            if self.start_time > pub_time.timestamp() or self.end_time < pub_time.timestamp():
                self.logger.info(f'时间错误：发布时间：{pub_time}')
                continue
            content_item['publish_time'] = pub_time.strftime('%Y-%m-%d %H:%M:%S')
            content_item['content'] = item.get('text', '').strip(' \u200b')
            source_list = re.findall('>(.*?)<', item.get('source', ''))
            content_item['source'] = source_list[0] if source_list else ''
            content_item['attitudes_count'] = item.get('attitudes_count', 0)
            content_item['comments_count'] = item.get('comments_count', 0)
            content_item['reposts_count'] = item.get('reposts_count', 0)
            geo = item.get('geo', {})
            lng, lat = '', ''
            if geo:
                lng, lat = geo['coordinates']
            content_item['lng'] = lng
            content_item['lat'] = lat
            content_item['content_type'] = 'article'
            content_item['search_id'] = self.search_id
            content_item['article_url'] = parse.urljoin('https://weibo.com/', f'{user_id}/{mid}')
            content_item['mblogid'] = mid
            yield content_item
            # if content_item['comments_count'] > 0:
            #     c_url = f_comment.format(self.token, item['id'], 1)
            #     yield Request(c_url, callback=self.parse_comment)

    def parse_comment(self, response: scrapy.http.Response, **kwargs):
        try:
            data = json.loads(response.text)
        except Exception:
            self.logger.error(f'数据解析异常：{response.url}')
            return
        article_id = re.findall('id=(\d+?)&', response.url)[0]
        total = data.get('total_number', 0)
        for i in range(2, 20):
            url = f_comment.format(self.token, article_id, i)
            yield Request(url, callback=self.parse)
        for item in data.get('comments', []):
            comment_item = items.SinaItem()
            comment_item['detail_id'] = item['id']
            comment_item['author'] = item.get('user', {}).get('name')
            profile_url = item.get('user', {}).get('profile_url', '')
            comment_item['author_url'] = parse.urljoin('https://weibo.com/', profile_url) if profile_url else ''
            comment_item['content_type'] = 'comment'
            try:
                pub_time = datetime.datetime.strptime(item.get('created_at', ''), '%a %b %d %H:%M:%S %z %Y')
            except Exception:
                pub_time = datetime.datetime.now()
            if self.start_time > pub_time.timestamp():
                self.logger.info(f'时间错误：发布时间：{pub_time}')
                continue
            comment_item['publish_time'] = pub_time.strftime('%Y-%m-%d %H:%M:%S')
            comment_item['content'] = item.get('text', '').strip(' \u200b')
            comment_item['search_id'] = self.search_id
            article_user_id = item['user']['id']
            mid = sina_utils.id2mid(article_id)
            comment_item['article_url'] = parse.urljoin('https://weibo.com/', f'{article_user_id}/{mid}')
            comment_item['attitudes_count'] = 0
            comment_item['comments_count'] = 0
            comment_item['reposts_count'] = 0
            yield comment_item
