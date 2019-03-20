# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class WeiboItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()  # 微博ID
    weibo_url = scrapy.Field()  # 微博URL
    user_id = scrapy.Field()  # 用户ID
    create_at = scrapy.Field()  # 微博发表时间
    like_num = scrapy.Field()  # 点赞数
    repost_num = scrapy.Field()  # 转发数
    comment_num = scrapy.Field()  # 评论数
    all_content = scrapy.Field()  # 微博内容
