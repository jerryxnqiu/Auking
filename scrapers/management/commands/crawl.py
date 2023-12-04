from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from scrapers.scrapers import settings as my_settings
from scrapers.scrapers.spiders.chemistwarehouseProducts import ChemistwarehouseProductsSpider
from scrapers.scrapers.spiders.targetLegoProducts import TargetLegoSpider

class Command(BaseCommand):
    help = 'Release spider'

    def handle(self, *args, **options):
        crawler_settings = Settings()
        crawler_settings.setmodule(my_settings)

        process = CrawlerProcess(settings=crawler_settings)

        # process.crawl(ChemistwarehouseProductsSpider)
        process.crawl(TargetLegoSpider)
        process.start()