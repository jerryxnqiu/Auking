from urllib.parse import urljoin
import scrapy
from scrapy.http import Request
import json
import re
import math

from scrapers.scrapers.items import ProductFromScrapyItem, ProductImageItem
from product.models import ProductLogisticsAuExpress, ProductLogisticsEWE


class ChemistwarehouseProductsSpider(scrapy.Spider):
    name = "chemistwarehouseProducts"
    allowed_domains = ["www.chemistwarehouse.com.au", "pds.chemistwarehouse.com.au"]

    custom_settings = {
        'ITEM_PIPELINES': {
            "scrapers.scrapers.pipelines.ScrapersPipeline": 300,
            "scrapers.scrapers.pipelines.CustomImageCWPipeline": 1,
        },
    }

    '''
    3 root categories
    /shop-online/256/health (3008)
    /shop-online/259/personal-care (7157)
    /shop-online/257/beauty (9516)
    '''
    start_urls = ["/shop-online/256/health", "/shop-online/259/personal-care", "/shop-online/257/beauty"]

    def spuGenerationFunction(self, productBrand, lv2BreadcrumbsName, lv3BreadcrumbsName, lv4BreadcrumbsName, lv5BreadcrumbsName):

        # print("productBrand", productBrand)
        # print("lv2BreadcrumbsName", lv2BreadcrumbsName)
        # print("lv3BreadcrumbsName", lv3BreadcrumbsName)
        # print("lv4BreadcrumbsName", lv4BreadcrumbsName)
        # print("lv5BreadcrumbsName", lv5BreadcrumbsName)

        if (productBrand != "") and (productBrand is not None):

            if (lv5BreadcrumbsName != "") and (lv5BreadcrumbsName is not None):
                spu = productBrand + "-" + lv5BreadcrumbsName
            elif (lv4BreadcrumbsName != "") and (lv4BreadcrumbsName is not None):
                spu = productBrand + "-" + lv4BreadcrumbsName
            elif (lv3BreadcrumbsName != "") and (lv3BreadcrumbsName is not None):
                spu = productBrand + "-" + lv3BreadcrumbsName
            else:
                spu = productBrand + "-" + lv2BreadcrumbsName
        
        else:

            if (lv5BreadcrumbsName != "") and (lv5BreadcrumbsName is not None):
                spu = lv5BreadcrumbsName
            elif (lv4BreadcrumbsName != "") and (lv4BreadcrumbsName is not None):
                spu = lv4BreadcrumbsName
            elif (lv3BreadcrumbsName != "") and (lv3BreadcrumbsName is not None):
                spu = lv3BreadcrumbsName
            else:
                spu = lv2BreadcrumbsName


        return spu


    def start_requests(self):

        print("============================start_requests===============================")

        # To loop through the start_urls
        for url in self.start_urls:
            
            chemauCode = url.split("/")[2]
        
            yield scrapy.Request(
                url=urljoin("https://www.chemistwarehouse.com.au", url),
                meta={
                    "playwright": True
                },
                callback=self.parseRootCategoryPage,
                cb_kwargs={
                    'chemauCode': chemauCode,
                    }
            )


    def parseRootCategoryPage(self, response, chemauCode):

        print("==========================parseRootCategoryPage==========================")
        print("=========================================================================")
        
        ###########################################################################################
        # To get the max quantity of product in the root category page
        maxQuantity = int(response.xpath("//div[@id='page_skinning']//div[@class='category-navigation-bar__results']/text()")[0].get().split(" ")[0])


        ###########################################################################################
        # To calculate the page quantity and last page product quantity
        quantityPerPage = 45
        if (maxQuantity % quantityPerPage) > 0:
            pageCount = maxQuantity // quantityPerPage + 1
        else:
            pageCount = maxQuantity // quantityPerPage


        ###########################################################################################
        # To construct the url, with "start_index" and "chemau20"
        for pageIndex in range(pageCount):

            start_index = pageIndex * quantityPerPage
            
            url = 'https://pds.chemistwarehouse.com.au/search'
            url += '?identifier=AU'
            url += '&fh_start_index=0'
            url += '&fh_location=//catalog01/en_AU/categories<{catalog01_chemau}/categories<{chemau20}'

            url = re.sub(r"(?<=fh_start_index=)\d+", str(start_index), url)
            url = re.sub(r"(?<=chemau)\d+", str(chemauCode), url)

            print(maxQuantity, start_index, url)

            ###########################################################################################
            # To construct the header
            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Origin': 'https://www.chemistwarehouse.com.au',
                'Pragma': 'no-cache',
                'Referer': 'https://www.chemistwarehouse.com.au/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-site',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
            }

            yield scrapy.Request(
                url=url,
                headers=headers,
                meta={
                    "playwright": True
                    },
                callback=self.parseRootCategoryPageAPI,
                cb_kwargs={
                    'headers': headers,
                    }
            )


    def parseRootCategoryPageAPI(self, response, headers):

        print("========================parseRootCategoryPageAPI=========================")
        print("=========================================================================")
        print("=========================================================================")

        cwHtmlContent = response.text

        # Find the start and end of the JSON data within the HTML content
        start_marker = '<pre style="word-wrap: break-word; white-space: pre-wrap;">'
        end_marker = '</pre>'

        start_index = cwHtmlContent.find(start_marker)
        end_index = cwHtmlContent.find(end_marker, start_index)

        if start_index != -1 and end_index != -1:
            # Extract the JSON data from the HTML content
            jsonData = cwHtmlContent[start_index + len(start_marker):end_index]

            # Parse the JSON data into a Python dictionary
            try:
                data = json.loads(jsonData)

                # Now 'data' contains the JSON data as a Python dictionary
                # You can access and work with the JSON data as needed
            except json.JSONDecodeError as e:
                self.logger.error(f'Failed to parse JSON: {e}')
        else:
            self.logger.warning('JSON data not found in the response')

        itemsSection = data['universes']['universe'][0]['items-section']['items']['item']

        for cwItem in itemsSection:
            
            # To initiate variables
            productId = ""
            productSecondId = ""
            productName = ""
            productBrand = ""
            productThumbnailImageUrl = ""
            productPrice = ""
            productPageUrl = ""
            productTotalVote = ""
            productStarRating = ""
            productIsPrescription = ""
            productIsUltraBeauty = ""
            
            productId = cwItem['id']
            productAttributes = cwItem['attribute']

            for productAttribute in productAttributes:
                
                if productAttribute['name'] == "secondid":
                    productSecondId = productAttribute['value'][0]['value']

                elif productAttribute['name'] == "name":
                    productName = productAttribute['value'][0]['value']

                elif productAttribute['name'] == "brand":
                    productBrand = productAttribute['value'][0]['value']
                
                elif productAttribute['name'] == "_thumburl":
                    productThumbnailImageUrl = productAttribute['value'][0]['value']
                
                elif productAttribute['name'] == "price_cw_au":
                    productPrice = productAttribute['value'][0]['value']

                elif productAttribute['name'] == "producturl":
                    productPageUrl = productAttribute['value'][0]['value']
                
                elif productAttribute['name'] == "bv_total_votes":
                    productTotalVote = productAttribute['value'][0]['value']
                
                elif productAttribute['name'] == "bv_star_rating":
                    productStarRating = productAttribute['value'][0]['value']
                
                elif productAttribute['name'] == "is_prescription":
                    productIsPrescription = productAttribute['value'][0]['value']

                elif productAttribute['name'] == "is_ultra_beauty":
                    productIsUltraBeauty = productAttribute['value'][0]['value']


            # If not the "UltraBeauty" product
            if (productIsUltraBeauty == "0") & (productIsPrescription == "0"):

                yield scrapy.Request(
                    url=productPageUrl,
                    headers=headers,
                    meta={
                        "playwright": True
                        },
                    callback=self.parseProductPage,
                    cb_kwargs={
                        'headers': headers,
                        'productId': productId,
                        'productSecondId': productSecondId,
                        'productName': productName,
                        'productBrand': productBrand,
                        'productThumbnailImageUrl': productThumbnailImageUrl,
                        'productPrice': productPrice,
                        'productTotalVote': productTotalVote,
                        'productStarRating': productStarRating,
                        }
                )


    def parseProductPage(self, response, headers, productId, productSecondId, productName, productBrand, productThumbnailImageUrl, productPrice, productTotalVote, productStarRating):

        print("=============================parseProductPage============================")
        print("=========================================================================")
        print("=========================================================================")
        print("=========================================================================")


        #####################################################################################################
        #####################################################################################################
        #####################################################################################################
        # To get the categories and construct "category", "subCategory" and "spu"
        lv1BreadcrumbsName = response.xpath('//div[@class="Main-Container"]//div[@class="breadcrumbs"]/a[2]/text()').get()
        lv2BreadcrumbsName = response.xpath('//div[@class="Main-Container"]//div[@class="breadcrumbs"]/a[3]/text()').get()
        lv3BreadcrumbsName = response.xpath('//div[@class="Main-Container"]//div[@class="breadcrumbs"]/a[4]/text()').get()
        lv4BreadcrumbsName = response.xpath('//div[@class="Main-Container"]//div[@class="breadcrumbs"]/a[5]/text()').get()
        lv5BreadcrumbsName = response.xpath('//div[@class="Main-Container"]//div[@class="breadcrumbs"]/a[6]/text()').get()


        #####################################################################################################
        #####################################################################################################
        #####################################################################################################
        cosmeticsListLv2Keywords = ["Cosmetics", "Beauty Accessories", "Fragrances"]

        # All under "Personal Care" Root Category
        if lv3BreadcrumbsName == "Baby Formula":
            category = "babyFormula"
            subCategory = lv4BreadcrumbsName
            spu = self.spuGenerationFunction(productBrand, lv2BreadcrumbsName, lv3BreadcrumbsName, lv4BreadcrumbsName, lv5BreadcrumbsName)

        elif (lv1BreadcrumbsName == "Personal Care") and (lv3BreadcrumbsName != "Baby Formula"):
            category = "dailyCare"
            subCategory = lv2BreadcrumbsName
            spu = self.spuGenerationFunction(productBrand, lv2BreadcrumbsName, lv3BreadcrumbsName, lv4BreadcrumbsName, lv5BreadcrumbsName)


        #####################################################################################################
        #####################################################################################################
        #####################################################################################################
        # All under "Health" Root Category
        elif lv2BreadcrumbsName == "Milk Supplements":
            category = "adultFormula"
            subCategory = lv2BreadcrumbsName
            spu = self.spuGenerationFunction(productBrand, lv2BreadcrumbsName, lv3BreadcrumbsName, lv4BreadcrumbsName, lv5BreadcrumbsName)

        elif lv3BreadcrumbsName == "Sustagen":
            category = "adultFormula"
            subCategory = lv4BreadcrumbsName
            spu = self.spuGenerationFunction(productBrand, lv2BreadcrumbsName, lv3BreadcrumbsName, lv4BreadcrumbsName, lv5BreadcrumbsName)

        elif lv3BreadcrumbsName == "Meal Replacements":
            category = "adultFormula"
            subCategory = lv3BreadcrumbsName
            spu = self.spuGenerationFunction(productBrand, lv2BreadcrumbsName, lv3BreadcrumbsName, lv4BreadcrumbsName, lv5BreadcrumbsName)

        elif lv2BreadcrumbsName == "Sports Nutrition":
            category = "food"
            subCategory = lv3BreadcrumbsName
            spu = self.spuGenerationFunction(productBrand, lv2BreadcrumbsName, lv3BreadcrumbsName, lv4BreadcrumbsName, lv5BreadcrumbsName)

        elif (lv1BreadcrumbsName == "Health") and (lv2BreadcrumbsName != "Milk Supplements") and (lv3BreadcrumbsName != "Sustagen") and (lv3BreadcrumbsName != "Meal Replacements") and (lv2BreadcrumbsName != "Sports Nutrition"):
            category = "health"
            subCategory = lv2BreadcrumbsName
            spu = self.spuGenerationFunction(productBrand, lv2BreadcrumbsName, lv3BreadcrumbsName, lv4BreadcrumbsName, lv5BreadcrumbsName)


        #####################################################################################################
        #####################################################################################################
        #####################################################################################################
        # All under "Beauty" Root Category
        elif lv2BreadcrumbsName in cosmeticsListLv2Keywords:
            category = "cosmetics"
            if (lv3BreadcrumbsName != "") or (lv3BreadcrumbsName is not None):
                subCategory = lv3BreadcrumbsName
            else:
                subCategory = lv2BreadcrumbsName
            spu = self.spuGenerationFunction(productBrand, lv2BreadcrumbsName, lv3BreadcrumbsName, lv4BreadcrumbsName, lv5BreadcrumbsName)

        elif (lv1BreadcrumbsName == "Beauty") and (lv2BreadcrumbsName not in cosmeticsListLv2Keywords):
            category = "skinCare"
            if (lv3BreadcrumbsName != "") or (lv3BreadcrumbsName is not None):
                subCategory = lv3BreadcrumbsName
            else:
                subCategory = lv2BreadcrumbsName
            spu = self.spuGenerationFunction(productBrand, lv2BreadcrumbsName, lv3BreadcrumbsName, lv4BreadcrumbsName, lv5BreadcrumbsName)

        else:
            category = "cosmetics"
            subCategory = lv1BreadcrumbsName
            spu = lv1BreadcrumbsName

        print(category, subCategory, spu)
        print(productId, productSecondId, productName, productBrand, productThumbnailImageUrl, productPrice, productTotalVote, productStarRating)


        # To get the product page images
        # get the image network path and save the picture
        productImageOriginalUrls = [productThumbnailImageUrl]

        # If it has valid image path
        if response.xpath('//div[@class="pi_slide"]'):
            
            for urlItem in response.xpath('//div[@class="pi_slide"]'):
                productImageOriginalUrls.append(urlItem.xpath('.//a/@href').get())

        # If it is just a placeholder and no image
        else:
            productImageOriginalUrls = [response.xpath('//div[@id="product_images"]//img/@src').get()]

        productImageNewUrls = []
        print(productImageOriginalUrls)
        for urlItem in productImageOriginalUrls:
            imageName = urlItem.split("/")[-1]
            productId = "AukingCW" + urlItem.split("/")[-2]
            productImageNewUrls.append("images/productSKU/" + productId + "/" + imageName)

        item = ProductImageItem()
        item['image_urls'] = productImageOriginalUrls

        yield item


        productPageAPIUrl = 'https://pds.chemistwarehouse.com.au/search?identifier=AU&fh_location=//catalog01/en_AU/categories%3C{catalog01_chemau}&fh_secondid=107625'
        productPageAPIUrl = re.sub(r"(?<=fh_secondid=)\d+", str(productSecondId), productPageAPIUrl)

        yield scrapy.Request(
                    url=productPageAPIUrl,
                    headers=headers,
                    meta={
                        "playwright": True
                        },
                    callback=self.parseProductPageAPI,
                    cb_kwargs={
                        'headers': headers,
                        'category': category, 
                        'subCategory': subCategory, 
                        'spu': spu,
                        'lv1BreadcrumbsName': lv1BreadcrumbsName,
                        'lv2BreadcrumbsName': lv2BreadcrumbsName,
                        'lv3BreadcrumbsName': lv3BreadcrumbsName,
                        'lv4BreadcrumbsName': lv4BreadcrumbsName, 
                        'lv5BreadcrumbsName': lv5BreadcrumbsName,
                        'productId': productId,
                        'productSecondId': productSecondId,
                        'productName': productName,
                        'productBrand': productBrand,
                        'productImageOriginalUrls': productImageOriginalUrls,
                        'productImageNewUrls': productImageNewUrls,
                        'productPrice': productPrice,
                        'productTotalVote': productTotalVote,
                        'productStarRating': productStarRating,
                        }
                )


    def parseProductPageAPI(self, response, headers, category, subCategory, spu,\
                            lv1BreadcrumbsName, lv2BreadcrumbsName, lv3BreadcrumbsName, lv4BreadcrumbsName, lv5BreadcrumbsName,\
                            productId, productSecondId, productName, productBrand, productImageOriginalUrls, productImageNewUrls,\
                            productPrice, productTotalVote, productStarRating):

        print("=============================parseProductPageAPI=========================")
        print("=========================================================================")
        print("=========================================================================")
        print("=========================================================================")

        cwHtmlContent = response.text

        # Find the start and end of the JSON data within the HTML content
        start_marker = '<pre style="word-wrap: break-word; white-space: pre-wrap;">'
        end_marker = '</pre>'

        start_index = cwHtmlContent.find(start_marker)
        end_index = cwHtmlContent.find(end_marker, start_index)

        if start_index != -1 and end_index != -1:
            # Extract the JSON data from the HTML content
            jsonData = cwHtmlContent[start_index + len(start_marker):end_index]

            # Parse the JSON data into a Python dictionary
            try:
                data = json.loads(jsonData)

                # Now 'data' contains the JSON data as a Python dictionary
                # You can access and work with the JSON data as needed
            except json.JSONDecodeError as e:
                self.logger.error(f'Failed to parse JSON: {e}')
        else:
            self.logger.warning('JSON data not found in the response')

        itemsSection = data['universes']['universe'][0]['items-section']["items"]["item"][0]['attribute'][4]['value'][0]

        #####################################################################################################
        #####################################################################################################
        #####################################################################################################
        item = ProductFromScrapyItem()

        # Straightforward assignment
        item["category"] = category
        item["subCategory"] = subCategory
        item["spu"] = spu
        item["lv1BreadcrumbsName"] = lv1BreadcrumbsName
        item["lv2BreadcrumbsName"] = lv2BreadcrumbsName
        item["lv3BreadcrumbsName"] = lv3BreadcrumbsName
        item["lv4BreadcrumbsName"] = lv4BreadcrumbsName
        item["lv5BreadcrumbsName"] = lv5BreadcrumbsName

        # Unique key
        item["sourceName"] = "CW"
        item["sourceNameAndId"] = productId
        
        item["name"] = productName
        item["brand"] = productBrand

        if lv2BreadcrumbsName == "Fragrances":
            description = ""
        else:
            description = data['universes']['universe'][0]['items-section']["items"]["item"][0]['attribute'][4]["value"][0]["value"]
        item["description"] = description

        item["cost"] = productPrice

        item["imageThumbNail"] = productImageNewUrls[0]
        item["imageProductPage"] = productImageNewUrls[1:]

        #####################################################################################################
        # To calculate the price, profit and exchange rate
        price = math.ceil(float(productPrice) * 1.1 * 4.8)
        item["price"] = price

        # To calculate the GST
        if category == "babyFormula" or category == "adultFormula" or "Honey" in productName or "honey" in productName:
            gst = 0
        else:
            gst = round(price / 11, 2)
        item["gst"] = gst
        

        #####################################################################################################
        # To derive product weight information
        sizePatternInProductName = r'\b\d+\s*(?:x|\s?kg|g|Capsules|Mini Tablets|Tablets|ml|mL|Pack|L|m)\b'
        sizePatternInDescription = r'&lt;p&gt;Size: (.*?)&lt;/p&gt;'
        patternMatchedInProductName = re.search(sizePatternInProductName, productName, re.IGNORECASE)
        patternMatchedInDescripption = re.search(sizePatternInDescription, description, re.IGNORECASE)
        
        packageSize = -1
        if patternMatchedInProductName:
            packageSize = patternMatchedInProductName.group()
            packageSize = packageSize.lstrip().rstrip()
            
        
        elif packageSize == -1 and patternMatchedInDescripption:
            packageSize = patternMatchedInDescripption.group(1)
            packageSize = packageSize.lstrip().rstrip()
            
        

        # To set weight to be 0.4Kg if found no package size information
        if packageSize == -1:
            unit = "件"
            if "Toothbrush" in productName:
                weight = 2
            else:
                weight = 0.4


        # To get the cases with "g, ml", ratio is 40% extra for weight
        elif re.match(r'(\d+)\s*(g|ml|mL)', packageSize):

            packageSizeMatch = re.match(r'(\d+)\s*(g|ml|mL)', packageSize)
            number = int(packageSizeMatch.group(1))
            unit = "罐/瓶"
            
            # To round up with 1 decimal point
            weight = math.ceil(number * 1.4 / 100) / 10


        # To get the cases with "Capsules|Tablets", assuming 4g each Capsule or Tablet
        elif re.match(r'(\d+)\s*(Capsules|Mini Tablets|Tablets|m)', packageSize):

            packageSizeMatch = re.match(r'(\d+)\s*(Capsules|Mini Tablets|Tablets|m)', packageSize)
            number = int(packageSizeMatch.group(1))
            unit = "盒"
            
            # To round up with 1 decimal point
            weight = math.ceil(number * 4 * 1.4 / 100) / 10


        # To get the cases with "Pack", assuming 0.3Kg each Pack
        elif re.match(r'(\d+)\s*(Pack)', packageSize):

            packageSizeMatch = re.match(r'(\d+)\s*(Pack)', packageSize)
            number = int(packageSizeMatch.group(1))
            unit = "盒/包"
            
            # To round up with 1 decimal point
            weight = number * 0.3


        # To get the cases with "Kg"
        elif re.match(r'(\d+)\s*(Kg|kg|L|l)', packageSize):

            packageSizeMatch = re.match(r'(\d+)\s*(Kg|kg|L|l)', packageSize)
            number = int(packageSizeMatch.group(1))
            unit = "罐/瓶"
            
            # To round up with 1 decimal point
            weight = number * 1.4
        
        # To set unit and weight if no match in above
        else:
            unit = "件"
            weight = 1


        # To make sure the weight is at least 0.4Kg
        try:
            if weight < 0.4:
                weight = 0.4
        except:
            weight = 0.4

        item["unit"] = unit
        item["weight"] = weight
        

        # Formula in cans
        if category == "babyFormula":
            item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="纯奶粉-婴儿/成人罐装牛奶粉/羊奶粉")
            item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="罐装奶粉")
        
        elif (category == "adultFormula") and ("1kg" not in productName):
            item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="纯奶粉-婴儿/成人罐装牛奶粉/羊奶粉")
            item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="罐装奶粉")
        


        # Formula in bags
        elif (category == "adultFormula") and ("1kg" in productName):
            item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="纯奶粉袋装-成人袋装牛奶粉")
            item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="袋装奶粉")
        


        # Food
        elif (category == "food") and (("Honey" in productName) or ("honey" in productName) or ("Elevit" in productName)):
            item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="纯保健品类-麦卢卡蜂蜜 Manuka / 男女爱乐维")
            item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="保健品/食品")
        
        elif (category == "food") and (("Honey" not in productName) and ("honey" not in productName) and ("Elevit" not in productName)):
            item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="纯食品类-婴儿食品 (米糊 / 米粉 / 果泥 / 米饼 / 泡芙 / 磨牙棒等)")
            item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="保健品/食品")



        # skinCare
        elif (category == "skinCare") and (price < 30):
            item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="纯护肤类-面霜 / 洗面奶 / 爽肤水 / 精华 / 眼霜 / 防晒霜【单瓶≤$30】")
            item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="洗护产品+保健品/食品+ 奶瓶，水杯，卫生巾，玩具，牙刷头，塑料餐具等杂货")

        elif (category == "skinCare") and (price >= 30):
            item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="纯护肤类-面霜 / 洗面奶 / 爽肤水 / 精华 / 眼霜 / 防晒霜【单瓶≤$50】")
            item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="洗护产品+保健品/食品+ 奶瓶，水杯，卫生巾，玩具，牙刷头，塑料餐具等杂货")



        # Cosmetics
        elif (category == "cosmetics") and (price < 20):
            item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="纯彩妆类-BB霜 / 眼影 / 眼线笔 / 粉饼 / 口红 / 睫毛膏等【单瓶≤$20】")
            item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="洗护产品+保健品/食品+ 奶瓶，水杯，卫生巾，玩具，牙刷头，塑料餐具等杂货")

        elif (category == "cosmetics") and (price >= 20):
            item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="纯彩妆类-BB霜 / 眼影 / 眼线笔 / 粉饼 / 口红 / 睫毛膏等【单瓶≤$30】")
            item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="洗护产品+保健品/食品+ 奶瓶，水杯，卫生巾，玩具，牙刷头，塑料餐具等杂货")



        # Health
        elif category == "health":
            item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="纯保健品类-普通保健品【特殊保健品除外】")
            item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="保健品/食品")



        # Daily Care
        elif (category == "dailyCare") and (("Shampoo" in productName) or ("Conditioner" in productName) or ("Body Wash" in productName)):
            item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="纯日用品类-沐浴露 / 洗发水 / 护发素 / 洗液 / 隐形眼镜清理液 等清洁用品")
            item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="洗护产品+保健品/食品+ 奶瓶，水杯，卫生巾，玩具，牙刷头，塑料餐具等杂货")


        elif (category == "dailyCare") and ("Power Toothbrush" in productName):
            item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="纯日用品类-电动牙刷 Oral B【价值不超$30，需要取出电池】")
            item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="小家电 ")

        else:
            item["logisticsCategoryAuExpress"] = ProductLogisticsAuExpress.objects.get(name="纯日用品类-绵羊油 / 普通牙刷 / 牙膏 / 木瓜膏")
            item["logisticsCategoryEWE"] = ProductLogisticsEWE.objects.get(name="洗护产品+保健品/食品+ 奶瓶，水杯，卫生巾，玩具，牙刷头，塑料餐具等杂货")

        yield item


