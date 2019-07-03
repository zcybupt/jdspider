# -*- coding: utf-8 -*-
import scrapy
import re
import json
from copy import deepcopy
from ..items import JdItem, CommentsItem


class ItemInfoSpider(scrapy.Spider):
    name = 'item_info'
    allowed_domains = ['jd.com']
    keyword = '手机'
    page = 1
    url = 'https://search.jd.com/Search?keyword=%s&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq=%s&page=%d&s=55&click=0'
    next_url = 'https://search.jd.com/s_new.php?keyword=%s&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&cid2=653&cid3=655&page=%d&scrolling=y&show_items=%s'
    comment_url = 'https://sclub.jd.com/comment/productPageComments.action?productId=%s&score=0&sortType=5&page=%d&pageSize=10&isShadowSku=0&fold=1'

    def start_requests(self):
        yield scrapy.Request(self.url % (self.keyword, self.keyword, self.page), callback=self.parse)

    def parse(self, response):
        ids = []
        for li in response.xpath('//*[@id="J_goodsList"]/ul/li'):
            item = JdItem()

            title = li.xpath('div/div[@class="p-name p-name-type-2"]/a/em/text()').extract_first()
            price = li.xpath('div/div[@class="p-price"]/strong/i/text()').extract_first()
            description = li.xpath('div/div/a/@title').extract_first()
            data_pid = li.xpath('@data-pid').extract_first()
            ids.append(''.join(data_pid))
            item_url = 'https:' + li.xpath('div/div[@class="p-name p-name-type-2"]/a/@href').extract_first()
            shop_name = li.xpath('div/div[@class="p-shop"]/span/a/text()').extract_first()
            shop_url = li.xpath('div/div[@class="p-shop"]/span/a/@href').extract_first()

            if shop_name is None or shop_url is None:
                continue
            shop_id = re.findall('\d+', shop_url)[0]
            shop_url = 'https:' + shop_url

            item['product_id'] = re.findall('\d+', item_url)[0]
            item['title'] = title
            item['price'] = price
            item['description'] = description
            item['item_url'] = item_url
            item['shop_id'] = shop_id
            item['shop_name'] = shop_name
            item['shop_url'] = shop_url

            comment_page = 0
            yield scrapy.Request(
                self.comment_url % (item['product_id'], comment_page),
                callback=self.comment_parse,
                meta={
                    'item': deepcopy(item),
                    'comment_page': comment_page
                })

        headers = {'referer': response.url}
        self.page += 1
        yield scrapy.Request(self.next_url % (self.keyword, self.page, ','.join(ids)),
                             callback=self.next_parse, headers=headers)

    def next_parse(self, response):
        for li in response.xpath('//li[@class="gl-item"]'):
            item = JdItem()
            title = li.xpath('div/div[@class="p-name p-name-type-2"]/a/em/text()').extract_first()
            price = li.xpath('div/div[@class="p-price"]/strong/i/text()').extract_first()
            description = li.xpath('div/div/a/@title').extract_first()
            item_url = 'https:' + li.xpath('div/div[@class="p-name p-name-type-2"]/a/@href').extract_first()
            shop_name = li.xpath('div/div[@class="p-shop"]/span/a/text()').extract_first()
            shop_url = li.xpath('div/div[@class="p-shop"]/span/a/@href').extract_first()

            if shop_name is None or shop_url is None:
                continue

            shop_id = re.findall('\d+', shop_url)[0]
            shop_url = 'https:' + shop_url

            item['product_id'] = re.findall('\d+', item_url)[0]
            item['title'] = title
            item['price'] = price
            item['description'] = description
            item['item_url'] = item_url
            item['shop_id'] = shop_id
            item['shop_name'] = shop_name
            item['shop_url'] = shop_url

            comment_page = 0
            yield scrapy.Request(
                self.comment_url % (item['product_id'], comment_page),
                callback=self.comment_parse,
                meta={
                    'item': deepcopy(item),
                    'comment_page': comment_page
                })

        if self.page < 200:
            self.page += 1
            yield scrapy.Request(self.url % (self.keyword, self.keyword, self.page), callback=self.parse)

    def comment_parse(self, response):
        item = response.meta['item']
        json_dict = json.loads(response.body.decode('gbk'))
        item['total_count'] = json_dict['productCommentSummary']['commentCount']
        item['good_rate'] = json_dict['productCommentSummary']['goodRateShow']
        item['general_rate'] = json_dict['productCommentSummary']['generalRate']
        item['poor_rate'] = json_dict['productCommentSummary']['poorRate']
        item['good_count'] = json_dict['productCommentSummary']['goodCount']
        item['general_count'] = json_dict['productCommentSummary']['generalCount']
        item['poor_count'] = json_dict['productCommentSummary']['poorCount']

        yield item

        maxpage = json_dict['maxPage']

        for i in range(len(json_dict['comments'])):
            comment = CommentsItem()
            comment['comment_id'] = json_dict['comments'][i]['guid']
            comment['product_id'] = response.meta['item']['product_id']
            comment['user_id'] = json_dict['comments'][i]['id']
            comment['user_name'] = json_dict['comments'][i]['nickname']
            comment['score'] = json_dict['comments'][i]['score']
            comment['content'] = json_dict['comments'][i]['content']
            comment['type'] = json_dict['comments'][i]['referenceName']
            comment['time'] = json_dict['comments'][i]['referenceTime']
            yield comment

        comment_page = response.meta['comment_page']
        comment_page += 1
        if comment_page < 100 and comment_page < maxpage:
            yield scrapy.Request(
                self.comment_url % (response.meta['item']['product_id'], comment_page),
                callback=self.comment_parse,
                meta={
                    'item': response.meta['item'],
                    'comment_page': comment_page
                }
            )
