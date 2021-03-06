import time
import traceback
from urllib import parse
from http import cookiejar
import json
import datetime

import scrapy
import requests
from scrapy import Request

from sina import settings, items, database


def get_rule_list():
    conn_pool = database.get_conn()
    cursor, conn = conn_pool.get_conn()
    sql = "select label, rule from label_list WHERE is_del=0;"
    cursor.execute(sql)
    return cursor.fetchall()


class SinaSpiderSpider(scrapy.Spider):
    name = 'sinaSpider'
    allowed_domains = ['weibo.com']
    start_urls = [settings.SINA_ACCOUNT_URL.format(int(time.time() * 1000))]
    cookies = {}

    def __init__(self, key_word=None, start_time='', end_time='',
                 search_id: int = 0, *args, **kwargs):
        super(SinaSpiderSpider, self).__init__(*args, **kwargs)
        self.logger.info(f'爬取关键字：{key_word}, {start_time}, {end_time}')
        self.start_time = datetime.datetime.fromtimestamp(int(start_time))
        self.end_time = datetime.datetime.fromtimestamp(int(end_time))
        self.urls = self.generate_url(key_word, self.start_time, self.end_time)
        self.search_id = search_id
        self.rule_list = get_rule_list()

    @staticmethod
    def generate_url(key_word: str, start_time: datetime.datetime,
                     end_time: datetime.datetime):
        """
        生成url
        """
        urls = []
        hours = int((end_time-start_time).total_seconds())//3600
        for i in range(hours+1):
            s_time = (start_time+datetime.timedelta(hours=i)).strftime('%Y-%m-%d-%H')
            e_time = (start_time+datetime.timedelta(hours=i+1)).strftime('%Y-%m-%d-%H')
            params = {
                'q': key_word,
                'typeall': 1,
                'timescope': f'custom:{s_time}:{e_time}',
                'suball': 1,
                'Refer': 'g'
            }
            base_url = f"https://s.weibo.com/weibo?{parse.urlencode(params, safe=':')}"
            urls.append(base_url)
        return urls

    @staticmethod
    def get_cookies():
        cookies_path = settings.COOKIES_PATH
        cookies = cookiejar.LWPCookieJar(cookies_path)
        cookies.load(ignore_discard=True)
        return {item.name: item.value for item in cookies}

    def start_requests(self):
        self.cookies = self.get_cookies()
        self.logger.info(f'cookies: {self.cookies}')
        for url in self.start_urls:
            yield Request(url, cookies=self.cookies, dont_filter=True)

    def parse(self, response: scrapy.http.Response, **kwargs):

        next_urls = response.xpath('//span[@class="list"]//li/a/@href')
        # self.logger.info(fr'响应为：{response.text}')
        if not next_urls and 'account.weibo.com' in response.url:
            self.logger.info(f'cookie 刷新成功，即将请求目标链接')
            self.logger.info(f'目标链接为：{self.urls}')
            for url in self.urls:
                yield Request(url, callback=self.parse)

        for next_url in next_urls:
            yield Request(response.urljoin(next_url.get()), callback=self.parse)

        for detail_url in response.xpath('//p[@class="from"]/a[1]/@href'):
            mblogid = detail_url.get().split('/')[-1].split('?')[0]
            detail_url = 'https://weibo.com/ajax/statuses/show?id={}'.format(mblogid)
            yield Request(detail_url, callback=self.parse_detail)

    def get_cate_list(self, content: str):
        """
        内容分类
        """
        cate_list = ','.join(item[0] for item in self.rule_list if re.findall(item[1], content))
        if not cate_list:
            cate_list = '其他'
        return cate_list

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
        publish_time = publish_time.replace(tzinfo=None)
        if self.start_time > publish_time or self.end_time < publish_time:
            self.logger.info(f'时间错误：发布时间：{publish_time}')
            return

        publish_time = publish_time.strftime('%Y-%m-%d %H:%M:%S')
        content = data.get('text_raw', '')
        source = data.get('source', '').split()
        attitudes_count = data.get('attitudes_count', 0)
        comments_count = data.get('comments_count', 0)
        reposts_count = data.get('reposts_count', 0)
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
        content_item['reposts_count'] = reposts_count
        content_item['lng'] = ''
        content_item['lat'] = ''
        content_item['cate_list'] = self.get_cate_list(content_item['content'])
        yield content_item

        comment_url = f'https://weibo.com/ajax/statuses/buildComments?is_reload=1&id={detail_id}' \
                      f'&is_show_bulletin=2&is_mix=0&count=40#{content_item["article_url"]}'
        yield Request(comment_url, callback=self.parse_comment)

    def parse_comment(self, response: scrapy.http.Response, **kwargs):
        try:
            data = json.loads(response.text).get('data', [])
        except Exception:
            self.logger.error(f'数据解析异常：{response.url}, {response.text}')
            return
        article_url = response.request.url.split("#")[-1]
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
            publish_time = publish_time.replace(tzinfo=None)
            if self.start_time > publish_time or self.end_time + \
                    datetime.timedelta(days=2) < publish_time:
                self.logger.info(f'时间错误：发布时间：{publish_time}')
                return
            publish_time = publish_time.strftime('%Y-%m-%d %H:%M:%S')
            content = item.get('text_raw', '')
            like_counts = item.get('like_counts', 0)
            comments_count = len(item.get('comments', []))

            content_item = items.SinaItem()
            content_item['author'] = author
            content_item['content_type'] = 'comment'
            content_item['author_url'] = author_url
            content_item['article_url'] = article_url
            content_item['publish_time'] = publish_time
            content_item['content'] = content
            content_item['search_id'] = self.search_id
            content_item['source'] = ''
            content_item['attitudes_count'] = like_counts
            content_item['comments_count'] = comments_count
            content_item['detail_id'] = comment_id
            content_item['mblogid'] = ''
            content_item['cate_list'] = self.get_cate_list(content)
            yield content_item
