# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.pipelines.images import ImagesPipeline
from itemadapter import ItemAdapter
from asgiref.sync import sync_to_async
from scrapers.scrapers.items import ProductFromScrapyItem

import hashlib
from scrapy.utils.python import get_func_args, to_bytes

from product.models import ProductFromScrapy

class ScrapersPipeline:

    sync_to_async
    def process_item(self, item, spider):
        if isinstance(item, ProductFromScrapyItem):
            item.save()
        return item

class CustomImageCWPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        imageName = request.url.split("/")[-1]
        productId = "AukingCW" + request.url.split("/")[-2]
        image_filename = f"{productId}/{imageName}"

        return image_filename

class CustomImageTGPipeline(ImagesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        imageName = request.url.split("?")[0].split("/")[-1] + ".webp"
        productId = item.get('metaValue', 'NoIdFolder')
        return f"{productId}/{imageName}.jpg"