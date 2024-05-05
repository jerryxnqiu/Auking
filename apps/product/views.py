from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.generic import View
from django_redis import get_redis_connection
from bocfx import bocfx
import math

from .models import ProductCategory, ProductSubCategory, ProductSKU, ProductSPU, ProductImage, ProductAddOnService,\
                    ProductLogisticsAuExpress, ProductLogisticsEWE, IndexProductBanner, IndexCategoryProductBanner, IndexPromotionBanner


### import logging
### logger = logging.getLogger(__name__)

### Create your views here.
### Homepage
class IndexView(View):
    """Homepage"""
    
    def get(self, request):
        """display"""

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        # To get the product category
        categories = ProductCategory.objects.all()

        # To get the homepage product banner
        productBanners = IndexProductBanner.objects.all().order_by('index')

        # To get the homepage promotion banner
        promotionBanners = IndexPromotionBanner.objects.all().order_by('index')

        cartCount = 0
        if request.user.is_authenticated:
            conn = get_redis_connection('default')
            cartKey = 'cart_%s' % request.user.id

            # Returns the number of fields contained in the hash stored at key.
            # HLEN key
            cartCount = conn.hlen(cartKey)


        # To get the homepage product display information as per category
        for category in categories:
            # If displayCategory is 0, the product category will be shown as title and 1 is image
            titleBanners = IndexCategoryProductBanner.objects.filter(category=category, displayCategory=0).order_by('index')
            imageBanners = IndexCategoryProductBanner.objects.filter(category=category, displayCategory=1).order_by('index')

            # To update the sku price with live exchange rate, 4.8 is the initial exchange rate used in Scrapy for database ingestion
            for imageBanner in imageBanners:
                imageBanner.sku.price = math.ceil(float(imageBanner.sku.price) / 4.8 * 10) / 10
                imageBanner.sku.priceCN = math.ceil(float(imageBanner.sku.price) * audExRate * 10) / 10

            category.titleBanners = titleBanners
            category.imageBanners = imageBanners

            # logger.debug('Processing category image URL: %s', category.image.url)

        # To get the product quantity in customer's shopping cart
        shoppingCartCount = 0

        # To summarize the response
        context = {
            'audExRate': audExRate,
            'categories': categories,
            'cartCount': cartCount,
            'productBanners': productBanners,
            'promotionBanners': promotionBanners
        }

        return render(request, 'index.html', context)


### Individual product page
class DetailView(View):
    """Product Detail Information Page"""
    
    def get(self, request, productId):

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

        try:
            sku = ProductSKU.objects.get(id=productId)
        except ProductSKU.DoesNotExist as e:
            return redirect(reverse('product:index'))

        # To update the sku price with live exchange rate, 4.8 is the initial exchange rate used in Scrapy for database ingestion
        sku.price = math.ceil(float(sku.price) / 4.8 * 10) / 10
        sku.priceCN = math.ceil(float(sku.price) * audExRate * 10) / 10

        # To get the product category
        categories = ProductCategory.objects.all()

        # To get the product comments
        # sku_order = OrderGoods.objects.filter(sku=sku).exclude(comment='')
        
        # To get the newest N product from the same category
        n = 2
        newSkus = ProductSKU.objects.filter(category=sku.category).order_by('-create_time')[:n]

        # To get the products from the same SPU
        sameSpuSkus = ProductSKU.objects.filter(spu=sku.spu).exclude(id=productId)

        # To get all the service for the product, and convert the price to RMB
        addOnServices = ProductAddOnService.objects.all()

        # To update the sku price with live exchange rate, 4.8 is the initial exchange rate used in Scrapy for database ingestion
        for addOnService in addOnServices:
            addOnService.price = math.ceil(float(addOnService.price) * 10) / 10
            addOnService.priceCN = math.ceil(float(addOnService.price) * audExRate * 10) / 10

        # To get all pictures of the product
        pictures = ProductImage.objects.filter(sku=sku)

        # To find the main picture location in the "pictures"
        pictures = list(pictures)
        index_to_move = None
        for index, picture in enumerate(pictures):
            if picture.image == sku.image:
                index_to_move = index
                break

        # To check if the specific item was found
        if index_to_move is not None:

            # To remove the item from its current position
            item_to_move = pictures.pop(index_to_move)

            # To insert the item at the first position
            pictures.insert(0, item_to_move)

        # Get information from Redis
        # Get the product quantity in the cart on Homepage
        cartCount = 0
        if request.user.is_authenticated:
            conn = get_redis_connection('default')
            cartKey = 'cart_%s' % request.user.id

            # Returns the number of fields contained in the hash stored at key.
            # HLEN key
            cartCount = conn.hlen(cartKey)

            # To add into the browsing history
            conn = get_redis_connection('default')
            historyKey = 'history_%s' % request.user.id
            
            # To remove the productId if exist, 
            # count > 0: Remove elements equal to element moving from head to tail.
            # count = 0: Remove all elements equal to element
            # count < 0: Remove elements equal to element moving from tail to head.
            # LREM key count element            
            conn.lrem(historyKey, 0, productId)
            
            # Insert all the specified values at the head of the list stored at key.
            # LPUSH key element [element ...]
            conn.lpush(historyKey, productId)

            # Trim an existing list so that it will contain only the specified range of elements specified.
            # LTRIM key start stopzaaz
            conn.ltrim(historyKey, 0, 4)

        skuDescription = sku.description.replace('&lt;', '<').replace('&gt;', '>')
        skuDescription = skuDescription.replace('&amp;', '&')

        context = {
            'audExRate': audExRate,
            'categories': categories,
            'sku': sku,
            'skuDescription': skuDescription,
            'addOnServices': addOnServices,
            'newSkus': newSkus,
            'sameSpuSkus': sameSpuSkus,
            'cartCount': cartCount,
            'pictures': pictures,
        }

        return render(request, 'detail.html', context)


### Grid view of products of a category
class ProductCategoryListView(View):
    """Category List Page"""

    def get(self, request, categoryName, page):

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000
        
        # To get the product category
        categories = ProductCategory.objects.all()

        try:
            category = ProductCategory.objects.get(name=categoryName)
        except ProductCategory.DoesNotExist as e:
            return redirect(reverse('product:index'))

        # To get the sorting method
        sort = request.GET.get('sort')
        if sort == 'price':
            skus = ProductSKU.objects.filter(category=category).order_by('price')
        elif sort == 'hot':
            skus = ProductSKU.objects.filter(category=category).order_by('-sales')
        else:
            sort = 'default'
            skus = ProductSKU.objects.filter(category=category).order_by('-id')


        # To separate skus into pages, "x" order per page
        orderPerPage = 90
        paginator = Paginator(skus, orderPerPage)
        
        # To get the content of page "x"
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # To get the contents on page "page"
        skusPage = paginator.page(page)

        # To update the sku price with live exchange rate, 4.8 is the initial exchange rate used in Scrapy for database ingestion
        for sku in skusPage:
            sku.price = math.ceil(float(sku.price) / 4.8 * 10) / 10
            sku.priceCN = math.ceil(float(sku.price) * audExRate * 10) / 10

        # To limit the display of page number to "5"
        # 1. If total less than 5, then just display [1 - page number]
        # 2. If current is on page 3，then display [1,2,3,4,5]
        # If current is on last 3 pages, then display [4,5,6,7,8] num_pages-4 to num_oages+1
        numPages = paginator.num_pages
        
        # 1
        if numPages < 5:
            pages = range(1, numPages + 1)
        
        # 2
        elif page <= 3:
            pages = range(1, 6)
        elif numPages - page <= 2:
            pages = range(numPages-4, numPages+1)
        else:
            pages = range(page - 2, page + 3)
            

        # To get the content through the page object
        # To get the new products
        newSkus = ProductSKU.objects.filter(category=category).order_by('-create_time')[:2]
        
        # To update the sku price with live exchange rate, 4.8 is the initial exchange rate used in Scrapy for database ingestion
        for sku in newSkus:
            sku.price = math.ceil(float(sku.price) / 4.8 * 10) / 10
            sku.priceCN = math.ceil(float(sku.price) * audExRate * 10) / 10


        # 获取首页购物车的数目
        cartCount = 0
        if request.user.is_authenticated:
            conn = get_redis_connection('default')
            cartKey = 'cart_%s' % request.user.id
            cartCount = conn.hlen(cartKey)

        context = {
            'audExRate': audExRate,
            "sort": sort,
            'category': category,
            'categories': categories,
            "skusPage": skusPage,
            'newSkus': newSkus,
            "cartCount": cartCount,
            "pages": pages,
        }

        return render(request, 'listCategory.html', context)


### Grid view of products of a subCategory
class ProductSubCategoryListView(View):
    """SubCategory List Page"""

    def get(self, request, subCategoryName, page):

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000
        
        # To get the product subCategory
        subCategories = ProductSubCategory.objects.all()

        try:
            subCategory = ProductSubCategory.objects.get(name=subCategoryName)
        except ProductSubCategory.DoesNotExist as e:
            return redirect(reverse('product:index'))

        # To get the sorting method
        sort = request.GET.get('sort')
        if sort == 'price':
            skus = ProductSKU.objects.filter(subCategory=subCategory).order_by('price')
        elif sort == 'hot':
            skus = ProductSKU.objects.filter(subCategory=subCategory).order_by('-sales')
        else:
            sort = 'default'
            skus = ProductSKU.objects.filter(subCategory=subCategory).order_by('-id')

        category = skus[0].category

        # To separate skus into pages, "x" order per page
        orderPerPage = 30
        paginator = Paginator(skus, orderPerPage)
        
        # To get the content of page "x"
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # To get the contents on page "page"
        skusPage = paginator.page(page)

        # To update the sku price with live exchange rate, 4.8 is the initial exchange rate used in Scrapy for database ingestion
        for sku in skusPage:
            sku.price = math.ceil(float(sku.price) / 4.8 * 10) / 10
            sku.priceCN = math.ceil(float(sku.price) * audExRate * 10) / 10
        
        # To limit the display of page number to "5"
        # 1. If total less than 5, then just display [1 - page number]
        # 2. If current is on page 3，then display [1,2,3,4,5]
        # If current is on last 3 pages, then display [4,5,6,7,8] num_pages-4 to num_oages+1
        numPages = paginator.num_pages
        
        # 1
        if numPages < 5:
            pages = range(1, numPages + 1)
        
        # 2
        elif page <= 3:
            pages = range(1, 6)
        elif numPages - page <= 2:
            pages = range(numPages-4, numPages+1)
        else:
            pages = range(page - 2, page + 3)
            

        # To get the content through the page object
        # To get the new products
        newSkus = ProductSKU.objects.filter(subCategory=subCategory).order_by('-create_time')[:2]
        
        # To update the sku price with live exchange rate, 4.8 is the initial exchange rate used in Scrapy for database ingestion
        for sku in newSkus:
            sku.price = math.ceil(float(sku.price) / 4.8 * 10) / 10
            sku.priceCN = math.ceil(float(sku.price) * audExRate * 10) / 10

        # 获取首页购物车的数目
        cartCount = 0
        if request.user.is_authenticated:
            conn = get_redis_connection('default')
            cartKey = 'cart_%s' % request.user.id
            cartCount = conn.hlen(cartKey)

        context = {
            'audExRate': audExRate,
            "sort": sort,
            'category': category,
            'subCategory': subCategory,
            'subCategories': subCategories,
            "skusPage": skusPage,
            'newSkus': newSkus,
            "cartCount": cartCount,
            "pages": pages,
        }

        return render(request, 'listSubCategory.html', context)


### Grid view of products of a spu
class ProductSPUListView(View):
    """SPU List Page"""

    def get(self, request, spuName, page):

        ### Global variable for RMB to AUD exchange rate
        audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000
        
        # To get the product spu
        spus = ProductSPU.objects.all()

        try:
            spu = ProductSPU.objects.get(name=spuName)
        except ProductSPU.DoesNotExist as e:
            return redirect(reverse('product:index'))

        # To get the sorting method
        sort = request.GET.get('sort')
        if sort == 'price':
            skus = ProductSKU.objects.filter(spu=spu).order_by('price')
        elif sort == 'hot':
            skus = ProductSKU.objects.filter(spu=spu).order_by('-sales')
        else:
            sort = 'default'
            skus = ProductSKU.objects.filter(spu=spu).order_by('-id')

        category = skus[0].category

        # To separate skus into pages, "x" order per page
        orderPerPage = 30
        paginator = Paginator(skus, orderPerPage)
        
        # To get the content of page "x"
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # To get the contents on page "page"
        skusPage = paginator.page(page)

        # To update the sku price with live exchange rate, 4.8 is the initial exchange rate used in Scrapy for database ingestion
        for sku in skusPage:
            sku.price = math.ceil(float(sku.price) / 4.8 * 10) / 10
            sku.priceCN = math.ceil(float(sku.price) * audExRate * 10) / 10

        # To limit the display of page number to "5"
        # 1. If total less than 5, then just display [1 - page number]
        # 2. If current is on page 3，then display [1,2,3,4,5]
        # If current is on last 3 pages, then display [4,5,6,7,8] num_pages-4 to num_oages+1
        numPages = paginator.num_pages
        
        # 1
        if numPages < 5:
            pages = range(1, numPages + 1)
        
        # 2
        elif page <= 3:
            pages = range(1, 6)
        elif numPages - page <= 2:
            pages = range(numPages-4, numPages+1)
        else:
            pages = range(page - 2, page + 3)
            

        # To get the content through the page object
        # To get the new products
        newSkus = ProductSKU.objects.filter(spu=spu).order_by('-create_time')[:2]

        # To update the sku price with live exchange rate, 4.8 is the initial exchange rate used in Scrapy for database ingestion
        for sku in newSkus:
            sku.price = math.ceil(float(sku.price) / 4.8 * 10) / 10
            sku.priceCN = math.ceil(float(sku.price) * audExRate * 10) / 10

        # 获取首页购物车的数目
        cartCount = 0
        if request.user.is_authenticated:
            conn = get_redis_connection('default')
            cartKey = 'cart_%s' % request.user.id
            cartCount = conn.hlen(cartKey)

        context = {
            'audExRate': audExRate,
            "sort": sort,
            'category': category,
            'spu': spu,
            'spus': spus,
            "skusPage": skusPage,
            'newSkus': newSkus,
            "cartCount": cartCount,
            "pages": pages,
        }

        return render(request, 'listSPU.html', context)