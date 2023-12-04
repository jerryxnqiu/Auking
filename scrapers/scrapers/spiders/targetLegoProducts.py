from urllib.parse import urljoin
import scrapy
from scrapy.http import Request
import json
import re
import math

from scrapers.scrapers.items import ProductFromScrapyItem, ProductImageItemTG
from product.models import ProductLogisticsAuExpress, ProductLogisticsEWE


class TargetLegoSpider(scrapy.Spider):
    name = "targetlegoproducts"
    allowed_domains = ["www.target.com.au", "assets.target.com.au"]

    custom_settings = {
        'ITEM_PIPELINES': {
            "scrapers.scrapers.pipelines.ScrapersPipeline": 300,
            "scrapers.scrapers.pipelines.CustomImageTGPipeline": 1,
        },
    }

    '''
    Taget Lego only has one entry
    /c/toys/lego/W152974
    '''
    start_urls = ["/c/toys/lego/W152974"]

    def start_requests(self):

        print("============================start_requests===============================")

        # To loop through the start_urls
        for url in self.start_urls:

            yield scrapy.Request(
                url=urljoin("https://www.target.com.au", url),
                meta={
                    "playwright": True
                },
                callback=self.parseHomePage,

            )


    def parseHomePage(self, response):

        print("============================parseLegoHomePage============================")
        print("=========================================================================")
        
        ###########################################################################################
        # To get the max quantity of product in the root category page
        maxQuantity = response.xpath("//*[@data-testid='plp-product-list-container']/div[1]/p/text()").get().split()[0]
        productItemList = response.xpath("//*[@data-testid='plp-product-list-container']/div[1]/div[2]/div")
        productItemQtyPerPage = len(productItemList)
        pageQty = math.ceil(int(maxQuantity) / productItemQtyPerPage)
        
        for pageIndex in range(pageQty):

            url = 'https://www.target.com.au/c/toys/lego/W152974?page={pageIndex}&sortBy=price&sortOrder=descending'
            url = re.sub(r"{pageIndex}", str(pageIndex + 1), url)

            print(url)

            yield scrapy.Request(
                url=url,
                meta={
                    "playwright": True
                    },
                callback=self.parseSummaryPage,
            )


    def parseSummaryPage(self, response):

        print("==========================parseLegoSummaryPage===========================")
        print("=========================================================================")
        print("=========================================================================")

        productItemList = response.xpath("//*[@data-testid='plp-product-list-container']/div[1]/div[2]/div")

        for productItem in productItemList:

            productUrl = productItem.xpath(".//div[1]/a/@href").get()
            
            productId = "AukingTGP" + productUrl.split("/")[-1]
            productSecondId = productId
            productName = productItem.xpath(".//div[3]/a/p/text()").get()
            productBrand = "Lego"
            productThumbnailImageUrl = productItem.xpath(".//div[1]/a/img/@src").get()
            productPrice = float(productItem.xpath(".//*[@data-testid='was-price']/p/text()").get().replace("$", ""))
            productPageUrl = productUrl

            if productPrice < 200:
            
                yield scrapy.Request(
                        url=productPageUrl,
                        meta={
                            "playwright": True
                            },
                        callback=self.parseProductPage,
                        cb_kwargs={
                            'productId': productId,
                            'productSecondId': productSecondId,
                            'productName': productName,
                            'productBrand': productBrand,
                            'productThumbnailImageUrl': productThumbnailImageUrl,
                            'productPrice': productPrice,
                            }
                    )


    def parseProductPage(self, response, productId, productSecondId, productName, productBrand, productThumbnailImageUrl, productPrice):

        print("=============================parseProductPage============================")
        print("=========================================================================")
        print("=========================================================================")
        print("=========================================================================")

        print(productName, productPrice)
        #####################################################################################################
        #####################################################################################################
        #####################################################################################################
        # To get and construct "subCategory"
        subCategory = response.xpath('//*[@data-testid="breadcrumb-list"]/li[4]/a/span/text()').get()
        
        descriptionSpan = response.xpath('//*[@data-testid="controls-details-panel"]/div[9]/div/div/div/div/span')
        featureSpan = response.xpath('//*[@data-testid="controls-details-panel"]/div[9]/div[2]/div/div/div/ul/li/span/ul')

        description = ""
        feature = ""
        for pTag in descriptionSpan.xpath('.//p'):
            # Extract text content of each <p> tag
            description += pTag.extract()

        for liTag in featureSpan.xpath('.//li'):
            # Extract text content of each <li> tag
            feature += liTag.extract()

        if len(description) == 0:

            descriptionSpan = response.xpath('//*[@data-testid="controls-details-panel"]/div[10]/div/div/div/div/span')
            description = ""
            for pTag in descriptionSpan.xpath('.//p'):
                # Extract text content of each <p> tag
                description += pTag.extract()
            
            featureSpan = response.xpath('//*[@data-testid="controls-details-panel"]/div[10]/div[2]/div/div/div/ul/li/span/ul')
            feature = ""
            for liTag in featureSpan.xpath('.//li'):
                # Extract text content of each <li> tag
                feature += liTag.extract()

        elif len(description) == 0:
            descriptionSpan = response.xpath('//*[@data-testid="controls-details-panel"]/div[10]/div/div/div/div/span')
            description = ""
            for pTag in descriptionSpan.xpath('.//div'):
                # Extract text content of each <div> tag
                description += pTag.extract()

            featureSpan = response.xpath('//*[@data-testid="controls-details-panel"]/div[10]/div[2]/div/div/div/ul/li/span/ul')
            feature = ""
            for liTag in featureSpan.xpath('.//li'):
                # Extract text content of each <li> tag
                feature += liTag.extract()

        description = description + "<br>" + feature

        # To get the product page images
        # get the image network path and save the picture
        productImageOriginalUrls = [productThumbnailImageUrl]

        for urlItem in response.xpath('//*[@data-testid="gallery-grid"]/div'):
            productImageOriginalUrls.append(urlItem.xpath('.//div[@data-testid="gallery-image"]/img/@src').get())

        productImageNewUrls = []
        for urlItem in productImageOriginalUrls:
            imageName = urlItem.split("?")[0].split("/")[-1] + ".webp"
            productImageNewUrls.append("images/productSKU/" + productId + "/" + imageName)

        item = ProductImageItemTG()
        item['image_urls'] = productImageOriginalUrls
        item['metaValue'] = productId

        yield item

        #####################################################################################################
        #####################################################################################################
        #####################################################################################################
        item = ProductFromScrapyItem()

        # Straightforward assignment
        item["category"] = "toy"
        item["subCategory"] = "Lego"
        item["spu"] = subCategory
        item["lv1BreadcrumbsName"] = "toy"
        item["lv2BreadcrumbsName"] = "Lego"
        item["lv3BreadcrumbsName"] = subCategory
        item["lv4BreadcrumbsName"] = subCategory
        item["lv5BreadcrumbsName"] = subCategory

        # Unique key
        item["sourceName"] = "CW"
        item["sourceNameAndId"] = productId
        
        item["name"] = productName
        item["brand"] = productBrand

        item["description"] = description

        item["cost"] = productPrice

        item["imageThumbNail"] = productImageNewUrls[0]
        item["imageProductPage"] = productImageNewUrls[1:]

        #####################################################################################################
        # To calculate the price, profit and exchange rate
        price = productPrice * 1.1 * 4.8
        item["price"] = price

        # To calculate the GST
        gst = round(price / 11, 2)
        item["gst"] = gst
        

        #####################################################################################################
        # To derive product weight information
        unit = "盒"

        pieceCountPatternInDescription = r'<li>Product Piece Count: (\d+)</li>'
        patternMatchedInDescripption = re.search(pieceCountPatternInDescription, description, re.IGNORECASE)
        
        pieceCount = -1
        if patternMatchedInDescripption:
            pieceCount = patternMatchedInDescripption.group(1)
            pieceCount = pieceCount.lstrip().rstrip()

        # To assume each piece of block is about 3g
        weight = math.ceil(float(pieceCount) * 0.003 * 10) / 10

        # To assume weight is 2kg if no piece of block information is available
        if pieceCount == -1:
            weight = 2

        item["unit"] = unit
        item["weight"] = weight


        #####################################################################################################
        # To derive product logistics information
        item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="玩具类-Lego / Building Blocks / Jelly Cat / 玩偶【单件≤$100】")
        item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="洗护产品+保健品/食品+ 奶瓶，水杯，卫生巾，玩具，牙刷头，塑料餐具等杂货")


        yield item


