# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SinaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    author = scrapy.Field()
    author_url = scrapy.Field()
    article_url = scrapy.Field()
    publish_time = scrapy.Field()
    content = scrapy.Field()
    search_id = scrapy.Field()
    source = scrapy.Field()
    attitudes_count = scrapy.Field()
    comments_count = scrapy.Field()
    detail_id = scrapy.Field()
    mblogid = scrapy.Field()
    content_type = scrapy.Field()
    reposts_count = scrapy.Field()
    lng = scrapy.Field()
    lat = scrapy.Field()
    cate_list = scrapy.Field()
