from django.core.management.base import BaseCommand
from product.models import updateIndexCategoryProductBanner

class Command(BaseCommand):
    help = 'To updates "IndexCategoryProductBanner" table from "productSKU" table'

    def handle(self, *args, **kwargs):
        # Call your update function here
        updateIndexCategoryProductBanner()