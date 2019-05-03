# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime
from .models import User, Course, session


class ShiyanlouPipeline(object):
    def process_item(self, item, spider):
        session.add(Course(**item))
        return item

    def close_spider(self, spider):
        session.commit()
