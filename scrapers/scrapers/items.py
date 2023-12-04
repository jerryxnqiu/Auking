# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy_djangoitem import DjangoItem
from product.models import ProductFromScrapy
from scrapy import Field
from scrapy import Item

class ProductFromScrapyItem(DjangoItem):
    # define the fields for your item here like:
    # name = scrapy.Field()
    django_model = ProductFromScrapy


class ProductImageItem(Item):
    image_urls = Field()
    images = Field()


class ProductImageItemTG(Item):
    image_urls = Field()
    images = Field()
    metaValue = Field()
    