import scrapy


class GithubSpider(scrapy.Spider):
    name = 'x'
    start_urls = ['https://github.com/login']

    def parse(self, response):
        token = response.xpath('//form/input[1]/@value').extract_first()
        return scrapy.FormRequest.from_response(
                response,
                formdata = {
                    'authenticity_token': token,
                    'login': 'xxxx@qq.com',
                    'password': 'xxxx'
                },
                callback = self.after_parse,
        )

    def after_parse(self, response):
        self.logger.error('into after_parse')
        self.logger.error(response.body)
        return scrapy.Request(
            url = 'https://github.com/xxx/xxx',
            callback = self.xxx
        )

    def xxx(self, response):
        print('-----------------------------------')
        print(response.css('li.commits span::text').extract_first().strip())
