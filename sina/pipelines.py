# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging

import traceback
import redis

from sina.database import get_conn
from sina import settings


class SinaPipeline:
    def __init__(self):
        self.connection_pool = get_conn()
        self.cursor, self.conn = None, None

    def process_item(self, item, spider):
        self.cursor, self.conn = self.connection_pool.get_conn()
        if item['content_type'] == 'article':
            sql = "insert into article_list (search_id, author, author_url," \
                  " publish_time, content, source, attitudes_count, article_url, " \
                  f" comments_count, detail_id, mblogid) value(%s, %s, %s, %s," \
                  f" %s, %s, %s, %s, %s, %s, %s)"

            params = (item['search_id'], item['author'], item['author_url'],
                      item['publish_time'], item['content'], item['source'],
                      item['attitudes_count'], item['article_url'],
                      item['comments_count'], item['detail_id'],
                      item['mblogid'])
        else:
            sql = "insert into comment_list (search_id, detail_id, author, " \
                  "author_url, publish_time, content, like_counts, comments_count)" \
                  " value(%s, %s, %s, %s, %s, %s, %s, %s)"
            params = (item['search_id'], item['detail_id'], item['author'],
                      item['author_url'], item['publish_time'], item['content'],
                      item['attitudes_count'], item['comments_count'])
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
        except Exception:
            logging.error(f'数据存储失败：{sql}, {params}, {traceback.format_exc()}')
        return item

    def close_spider(self, spider):
        if self.cursor is not None:
            self.cursor.close()
            self.conn.close()
        conn = redis.Redis(
            host=settings.REDIS_SETTING['HOST'],
            port=settings.REDIS_SETTING['PORT'],
            password=settings.REDIS_SETTING['PASSWORD'])
        conn.rpush(settings.FINISHED_LIST_KEY, spider.search_id)