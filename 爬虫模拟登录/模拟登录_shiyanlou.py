import scrapy, json


class CoursesSpider(scrapy.Spider):
    name = 'courses'

    def start_requests(self):
        return [scrapy.Request(
            url = 'https://www.shiyanlou.com/api/v2/auth/login',
            method = 'POST',
            body = json.dumps({
                'login': 'xxxx@qq.com',
                'password': 'xxxx'
            }),
            headers = {
                'Content-Type':'application/json;charset=UTF-8',
            },
            callback = self.after_parse
        )]

    def after_parse(self, response):
        return scrapy.Request(
            url = 'https://www.shiyanlou.com/users/xxxx',
            callback = self.parse_after_login
        )

    def parse_after_login(self, response):
        yield {
            '累计实验次数': response.xpath('//ul[@class="user-lab-info-box"]/li[2]'
                '//li[2]/text()').extract_first().split()[1],
            '有效学习时间': response.xpath('//ul[@class="user-lab-info-box"]/li[3]'
                '//li[2]/text()').extract_first().split()[1]
        }
