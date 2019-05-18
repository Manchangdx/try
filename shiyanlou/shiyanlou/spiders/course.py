# -*- coding: utf-8 -*-
import scrapy
from shiyanlou.items import RepositoryItem


class CourseSpider(scrapy.Spider):
    name = 'course'
    start_urls = ['https://github.com/shiyanlou?tab=repositories']

    def parse(self, response):
        for course in response.xpath('.//div[@class="col-9 d-inline-block"]'):
            item = RepositoryItem(
                name = course.xpath('.//h3/a/text()').extract_first().strip(),
                update_time=course.css('relative-time::attr(datetime)'
                    ).extract_first()
            )
            course_url = course.xpath('.//h3/a/@href').extract_first()
            full_url=response.urljoin(course_url)
            request=scrapy.Request(full_url,self.parse_three)
            request.meta['item']=item
            yield request
        next_page_url = response.xpath('//div[@class="BtnGroup"]/a/@href'
            ).extract()[-1]
        yield response.follow(next_page_url, callback=self.parse)

    def parse_three(self,response):
        item = response.meta['item']
        print('-------------------------------', response.url)
        if response.xpath('//ul[@class="numbers-summary"]'):
            item['commits'] = response.css('span.num::text').extract()[0]
            item['branches'] = response.css('span.num::text').extract()[1]
            item['releases'] = response.css('span.num::text').extract()[2]
            yield item
