import time
import traceback
from urllib import parse
from http import cookiejar
import json
import datetime

import scrapy
import requests
from scrapy import Request

from sina import settings, items


class SinaSpiderSpider(scrapy.Spider):
    name = 'sinaSpider'
    allowed_domains = ['weibo.com']
    start_urls = [settings.SINA_ACCOUNT_URL.format(int(time.time() * 1000))]
    cookies = {}

    def __init__(self, key_word=None, start_time='', end_time='',
                 search_id: int = 0, *args, **kwargs):
        super(SinaSpiderSpider, self).__init__(*args, **kwargs)
        self.logger.info(f'爬取关键字：{key_word}, {start_time}, {end_time}')
        self.urls = self.generate_url(key_word, start_time, end_time)
        self.search_id = search_id

    @staticmethod
    def generate_url(key_word: str, start_time: str, end_time: str):
        """
        生成url
        """
        params = {
            'q': key_word,
            'typeall': 1,
            'timescope': f'custom:{start_time}:{end_time}',
            'suball': 1,
            'Refer': 'g'
        }
        base_url = f"https://s.weibo.com/weibo?{parse.urlencode(params, safe=':')}"
        return [base_url]

    @staticmethod
    def get_cookies():
        cookies_path = settings.COOKIES_PATH
        cookies = cookiejar.LWPCookieJar(cookies_path)
        cookies.load(ignore_discard=True)
        return {item.name: item.value for item in cookies}

    def start_requests(self):
        self.cookies = self.get_cookies()
        for url in self.start_urls:
            yield Request(url, cookies=self.cookies)

    def parse(self, response: scrapy.http.Response, **kwargs):

        next_urls = response.xpath('//span[@class="list"]//li/a/@href')
        if not next_urls and 'account.weibo.com' in response.url:
            self.logger.info(f'cookie 刷新成功，即将请求目标链接')
            self.logger.info(f'目标链接为：{self.urls}')
            for url in self.urls:
                yield Request(url, callback=self.parse)

        for next_url in next_urls[:1]:
            yield Request(response.urljoin(next_url.get()), callback=self.parse)

        for detail_url in response.xpath('//p[@class="from"]/a[1]/@href'):
            mblogid = detail_url.get().split('/')[-1].split('?')[0]
            detail_url = 'https://weibo.com/ajax/statuses/show?id={}'.format(mblogid)
            yield Request(detail_url, callback=self.parse_detail)

    def parse_detail(self, response: scrapy.http.Response, **kwargs):
        try:
            data = json.loads(response.text)
        except Exception:
            self.logger.error(f'数据解析异常：{response.url}, {response.text}')
            return
        mblogid = data.get('mblogid', '')
        user_id = data.get('user', {}).get('id', '')
        detail_id = data.get('mid', '')
        author = data.get('user', {}).get('screen_name', '')
        profile_url = data.get('user', {}).get('profile_url', '')
        author_url = parse.urljoin('https://weibo.com/', profile_url) if profile_url else ''
        try:
            publish_time = datetime.datetime.strptime(data.get('created_at', ''), '%a %b %d %H:%M:%S %z %Y')
        except Exception:
            publish_time = datetime.datetime.now()
        publish_time = publish_time.strftime('%Y-%m-%d %H:%M:%S')
        content = data.get('text_raw', '')
        source = data.get('source', '').split()
        attitudes_count = data.get('attitudes_count', 0)
        comments_count = data.get('comments_count', 0)
        content_item = items.SinaItem()
        content_item['author'] = author
        content_item['content_type'] = 'article'
        content_item['author_url'] = author_url
        content_item['article_url'] = f"https://weibo.com/{user_id}/{mblogid}"
        content_item['publish_time'] = publish_time
        content_item['content'] = content
        content_item['search_id'] = self.search_id
        content_item['source'] = source[0] if source else ''
        content_item['attitudes_count'] = attitudes_count
        content_item['comments_count'] = comments_count
        content_item['detail_id'] = detail_id
        content_item['mblogid'] = mblogid
        yield content_item

        comment_url = 'https://weibo.com/ajax/statuses/buildComments?is_reload=1&id={}' \
                      '&is_show_bulletin=2&is_mix=0&count=40'.format(detail_id)
        yield Request(comment_url, callback=self.parse_comment)

    def parse_comment(self, response: scrapy.http.Response, **kwargs):
        try:
            data = json.loads(response.text).get('data', [])
        except Exception:
            self.logger.error(f'数据解析异常：{response.url}, {response.text}')
            return

        for item in data:
            comment_id = item.get('mid', '')
            author = item.get('user', {}).get('screen_name', '')
            profile_url = item.get('user', {}).get('profile_url', '')
            author_url = parse.urljoin('https://weibo.com/', profile_url) if profile_url else ''
            try:
                publish_time = datetime.datetime.strptime(
                    item.get('created_at', ''), '%a %b %d %H:%M:%S %z %Y')
            except Exception:
                publish_time = datetime.datetime.now()
            publish_time = publish_time.strftime('%Y-%m-%d %H:%M:%S')
            content = item.get('text_raw', '')
            like_counts = item.get('like_counts', '')
            comments_count = len(item.get('comments', []))

            content_item = items.SinaItem()
            content_item['author'] = author
            content_item['content_type'] = 'comment'
            content_item['author_url'] = author_url
            content_item['article_url'] = ''
            content_item['publish_time'] = publish_time
            content_item['content'] = content
            content_item['search_id'] = self.search_id
            content_item['source'] = ''
            content_item['attitudes_count'] = like_counts
            content_item['comments_count'] = comments_count
            content_item['detail_id'] = comment_id
            content_item['mblogid'] = ''
            yield content_item
