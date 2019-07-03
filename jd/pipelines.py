# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from .items import JdItem, CommentsItem
from .settings import MYSQL_HOST, MYSQL_DBNAME, MYSQL_USER, MYSQL_PASSWD
import pymysql as pq


class JdPipeline(object):
    def __init__(self):
        self.item_num = 0
        self.comment_num = 0
        self.conn = pq.connect(
            host=MYSQL_HOST,
            db=MYSQL_DBNAME,
            user=MYSQL_USER,
            passwd=MYSQL_PASSWD,
            charset='utf8'
        )
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        try:
            if isinstance(item, JdItem):
                sql = 'INSERT INTO jd.items_info(product_id, title,price, description, item_url, shop_id, shop_name, shop_url, ' \
                      'total_count, good_rate, general_rate, poor_rate, good_count, general_count, poor_count) ' \
                      'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                self.cur.execute(sql, (
                    item['product_id'],
                    item['title'],
                    item['price'],
                    item['description'],
                    item['item_url'],
                    item['shop_id'],
                    item['shop_name'],
                    item['shop_url'],
                    item['total_count'],
                    item['good_rate'],
                    item['general_rate'],
                    item['poor_rate'],
                    item['good_count'],
                    item['general_count'],
                    item['poor_count'],
                ))
                self.conn.commit()
                self.item_num += 1
                print('JdItem ==> total number: ' + str(self.item_num) + '\n')
            elif isinstance(item, CommentsItem):
                sql = 'INSERT INTO jd.comments_info(comment_id ,product_id, user_id, user_name, score, content, type, time)' \
                      'VALUES(%s, %s, %s, %s, %s, %s, %s, %s)'
                self.cur.execute(sql, (
                    item['comment_id'],
                    item['product_id'],
                    item['user_id'],
                    item['user_name'],
                    item['score'],
                    item['content'],
                    item['type'],
                    item['time']
                ))
                self.conn.commit()
                self.comment_num += 1
                print('CommentsItem ==> total number: ' + str(self.comment_num) + '\n')
        except pq.err.IntegrityError:
            print("=====>>> 已去重 <<<====")


def close_spider(self, spider):
    self.cur.close()
    self.conn.close()
