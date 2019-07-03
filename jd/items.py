# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdItem(scrapy.Item):
    product_id = scrapy.Field()
    title = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    item_url = scrapy.Field()
    shop_id = scrapy.Field()
    shop_name = scrapy.Field()
    shop_url = scrapy.Field()
    total_count = scrapy.Field()
    good_rate = scrapy.Field()
    general_rate = scrapy.Field()
    poor_rate = scrapy.Field()
    good_count = scrapy.Field()
    general_count = scrapy.Field()
    poor_count = scrapy.Field()


class CommentsItem(scrapy.Item):
    comment_id = scrapy.Field()
    product_id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    score = scrapy.Field()
    content = scrapy.Field()
    type = scrapy.Field()
    time = scrapy.Field()
