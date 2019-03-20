# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class WeiboPipeline(object):
    def open_spider(self, spider):
        self.coon = pymongo.MongoClient(host='106.15.204.56')

    def process_item(self, item, spider):
        self.coon.xinlang.weibo.insert_one(item)

        return item

    def close_spider(self, spider):
        self.coon.close()
