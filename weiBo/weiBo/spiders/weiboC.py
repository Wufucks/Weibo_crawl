# -*- coding: utf-8 -*-
import scrapy
import re
from .utils import time_fix
import datetime

Cookies = {
    'ALF': '1555566750',
    '_T_WM': 'ad17813365183ec5c2b6fba4544683d5 ',
    'SUB': '_2A25xlJSwDeRhGeVG6FQX9i_JzDyIHXVTdjz4rDV6PUJbkdANLXfMkW1NT7o88IDKUDFLJv5Yrc71bixMgVncTMWr ',
    'SUHB': '0FQbL3glNgOxZO; SCF=Am8CPZ6hEZKb2d9k2Y3I0vu8LdeeJEAz0MZt2WDISOyvpg3lItPF84hAr3csjXB84eSiVQQ-9l0nIiEKYFcaR4s. ',
    'SSOLoginState': '1552999648',
    'MLOGIN': '1',
    'WEIBOCN_FROM': '1110106030',
    'XSRF-TOKEN': '4adcea',
    'M_WEIBOCN_PARAMS': 'luicode%3D10000011%26lfid%3D1076035781311106%26fid%3D1076035781311106%26uicode%3D10000011'}
header = {
    'Host': 'weibo.cn',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.6 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh,zh-CN;q=0.9,en;q=0.8',
}


class WeibocSpider(scrapy.Spider):
    name = 'weiboC'
    allowed_domains = ['weibo.cn']
    start_urls = ['http://weibo.cn/u/5781311106?page=1',
                  ]

    def start_requests(self):
        # for i in range(1, 29):
        url = 'http://weibo.cn/u/5781311106?page=1'
        yield scrapy.Request(url=url,
                             cookies=Cookies, headers=header, callback=self.parse, dont_filter=True)

    def parse(self, response):

        if response.url.endswith('page=1'):
            page_nums = re.search(r'/(\d+)页', response.text)
            if page_nums:
                page_nums = int(page_nums.group(1))
                for page_num in range(2, page_nums + 1):
                    page_url = response.url.replace('page=1', 'page={}'.format(page_num))
                    yield scrapy.Request(url=page_url, callback=self.parse, dont_filter=True, meta=response.meta)

        weibo_nodes = response.xpath('//div[@class="c" and @id]')
        for weibo_node in weibo_nodes:
            try:
                item = {}
                # 抓取时间
                item['crawl_time'] = datetime.datetime.now()
                # 转发url
                repost_url = weibo_node.xpath('.//a[contains(text(),"转发[")]/@href').extract()[0]

                repost_id = re.search(r'/repost/(.*?)\?uid=(\d+)', str(repost_url))
                # 单条微博url
                item['weibo_url'] = 'https://weibo.cn{}'.format(repost_id.group(0))
                # 用户ID
                item['user_id'] = repost_id.group(2)
                # ID
                item['_id'] = '{}_{}'.format(repost_id.group(2), repost_id.group(1))
                # 时间
                create_time_info = weibo_node.xpath('.//span[@class="ct"]/text()').extract()[-1]
                if '来自' in create_time_info:
                    item['create_at'] = time_fix(create_time_info.split('来自')[0].strip())
                else:
                    item['create_at'] = time_fix(create_time_info.strip())
                # 点赞数
                like_num = weibo_node.xpath('.//a[contains(text(),"赞[")]/text()').extract()[-1]
                item['like_num'] = int(re.search('\d+', str(like_num)).group())

                # 转发数
                repost_num = weibo_node.xpath('.//a[contains(text(),"转发[")]/text()').extract()[-1]
                item['repost_num'] = int(re.search(r'\d+', repost_num).group())

                # 评论数
                comment_num = \
                    weibo_node.xpath('.//a[contains(text(),"评论[")and not(contains(text(),"原文"))]/text()').extract()[-1]
                item['comment_num'] = int(re.search(r'\d+', str(comment_num)).group())

                content_node = weibo_node.xpath('.//span[@class="ctt"]')[0]
                all_content_link = content_node.xpath(r'.//a[text()="全文"]/@href').extract()
                if all_content_link:
                    all_content_link = 'http://weibo.cn' + str(all_content_link[0])
                    yield scrapy.Request(url=all_content_link, callback=self.parse_content, priority=1,
                                         meta={'item': item})
                else:
                    all_content = content_node.xpath('string(.)').extract_first().replace('\u200b', '')
                    item['all_content'] = all_content[0:]
                    yield item

            except Exception as e:
                self.logger.error(e)

    def parse_content(self, response):
        item = response.meta['item']
        content_node = response.xpath('.//div[@id="M_"]//span[@class="ctt"]')[0]
        all_content = content_node.xpath('string(.)').replace('\u200b', '').extract().strip()
        print(all_content)
        item['all_content'] = all_content[0:]
        yield item
