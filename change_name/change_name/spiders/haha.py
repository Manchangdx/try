# -*- coding: utf-8 -*-
import scrapy
from ..items import ChangeNameItem

class HahaSpider(scrapy.Spider):
    name = 'haha'
    start_urls = ['http://shiyanlou.com/courses']

    def parse(self, response):
        item = ChangeNameItem()
        item['imgurl'] = response.css('div.course-img img::attr(src)').extract()
        item['imgname'] = response.css('div.course-img img::attr(alt)').extract()
        yield item
