from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request

class ChangeNamePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        for i in item['imgurl']:
            yield Request(i, meta={'name': item['imgname'][item['imgurl'].index(i)]})

    def file_path(self, request, response=None, info=None):
        return request.meta['name'] + '.jpg'
