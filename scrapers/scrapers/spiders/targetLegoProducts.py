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
        print(len(productItemList))

        cookies = {
                    't_geo_country': 'AU',
                    't_geo_region': 'NSW',
                    't_geo_city': 'SYDNEY',
                    'rxVisitor': '1697203337959B5559338HDQ87Q5QSM73GIK4IHAH3D98',
                    'optimizelyEndUserId': 'oeu1697203338222r0.22459335210273412',
                    'dtSa': '-',
                    'rxvt': '1697205138447|1697203337960',
                    'dtPC': '-92$403337956_380h5vBOFPEPCAMUUJRPKAHEQUEFALCCWFDORS-0e0',
                    'dtCookie': 'v_4_srv_2_sn_SGO8SM4GURHV0EO2GOM326N7RGV3ET82_perc_100000_ol_0_mul_1_app-3Ac4c275d395d264a6_0',
                    'x-target': 'web',
                    't_psn': '5286',
                    't_pc': 'Unsw Sydney, 2052',
                    't_hd_pc': '2052',
                    't_cookie_accept': 'true',
                    '_gcl_au': '1.1.2109328798.1697203339',
                    'spl-declined': 'true',
                    '_scid': 'eabff028-3dd3-4541-8887-7818de54df32',
                    'PAC': 'b4b2671e-4137-4fb1-b7b7-09f028a898ed',
                    '_evga_f19e': '{%22uuid%22:%22994a3c3f15c0d107%22}',
                    '_sfid_7e2f': '{%22anonymousId%22:%22994a3c3f15c0d107%22%2C%22consents%22:[]}',
                    '_fbp': 'fb.2.1697203340115.996261157',
                    'ConstructorioID_client_id': 'd4575621-0a8e-4418-96f4-37b2388c5ebc',
                    '_tt_enable_cookie': '1',
                    '_ttp': 'VmxyaB8UcEmsv6JCOVRnDCXLcz9',
                    'crl8.fpcuid': '77a58f8d-a6a7-4edd-95f0-989b24f09411',
                    '_pin_unauth': 'dWlkPVpHWTRabUV5TnpndFl6QXhOaTAwTkRGaExXSmxZMlF0TVRNMFlUQmhNbVppWVRCaA',
                    '_cc': 'AYJSKW0IwlczjHdT3upUYaje',
                    '_cid_cc': 'AYJSKW0IwlczjHdT3upUYaje',
                    'FPID': 'FPID2.3.%2BWMM1qxVphO1XLSj1xCYUuhuZi5ezjTOj%2B7USa5d%2FNg%3D.1697203339',
                    'F5CM_view_help': 'false',
                    'isUir': 'on',
                    '_hjSessionUser_1847403': 'eyJpZCI6ImE0NjdlOTczLWY4YTMtNWEyMi1iNzFiLTliMzc1MmQ2MGM1ZCIsImNyZWF0ZWQiOjE2OTcyMDMzNDAyNzksImV4aXN0aW5nIjp0cnVlfQ==',
                    '__prz_uid': '267eecab-d512-4169-9797-8217312fb3cd',
                    'ak_fg_stale': '1',
                    '_ga_37WL4RRR1H': 'deleted',
                    '_gid': 'GA1.3.1205774904.1703166042',
                    '_sctr': '1%7C1703163600000',
                    'bm_sz': 'F2AB3E5A2DF3A2DDA29A81576435FA1F~YAAQDwg+F6EOS26MAQAAkT4mkRaUEfdXipihuvHfUcVql0mwIaiTvCkmVzVqng29XAZataqaXiUFHZtyo11Bm5Nyj9Gln/Ambl+zngWmuCFx0vAThF50piGTbYT2/ma4MbuBSUE36bRnazVN508MbEVSzZ8I4QBLA7VkvBaou5LvZyTSZvcVFOPt0LZDhusKPYmISCfX/i868T6dSoJG9BmvFA3TObUp9fhrjBUOXcDX39OcyYLcHlZQUpmobmWqRNB7YjQfJzaxpDj9d7nGjX8/HYKS7N5LF1Fk3n0jLmUHUSBdP8M=~4605251~4605238',
                    'JSESSIONID': 'NWNhZjRiOGEtOTVmOS00NmYyLTliNDEtNzY5YWVlZjkzMGY2',
                    '_uetsid': '89659c10a00611ee8ae07147f3d1f4b2',
                    '_uetvid': '897de0e069cb11ee9afa6761f1c86b2b',
                    '_clck': 'tsbu2f%7C2%7Cfhr%7C0%7C1381',
                    'FPLC': 'kG6cV%2BoMsQK7GGpfhIZct10c%2BP1S4Zg93F1OcG3xxYQ1m2ojmaBNXEL152E6%2BptY%2Bi0duUN2wtTidPaMkcIByCFm87Rb%2BO8SdUymTZHW0Je7I2%2BcUyOsa887bh11tQ%3D%3D',
                    '_clsk': 'ohmj9p%7C1703242255303%7C1%7C1%7Cr.clarity.ms%2Fcollect',
                    'AKA_A2': 'A',
                    'AWSALB': '54WnngJMq1xiDN4qDAPT2mlMECvFhqJoanplYsISgRyX4uRlaU00am8UGNY4nUdcHFqrna7LfKhI4rF5wsd0XYhI7qKCkN/cFKE8iPifLh3Tf6mmIh3oxQX31axg',
                    'AWSALBCORS': '54WnngJMq1xiDN4qDAPT2mlMECvFhqJoanplYsISgRyX4uRlaU00am8UGNY4nUdcHFqrna7LfKhI4rF5wsd0XYhI7qKCkN/cFKE8iPifLh3Tf6mmIh3oxQX31axg',
                    '_ga': 'GA1.3.706132585.1697203339',
                    '_scid_r': 'eabff028-3dd3-4541-8887-7818de54df32',
                    '_gat_UA-7927216-1': '1',
                    '_ga_37WL4RRR1H': 'GS1.1.1703250672.20.0.1703250674.58.0.0',
                    'ak_bmsc': 'C9809DC54044352E934E21E77AE054A9~000000000000000000000000000000~YAAQF8bOF9YJX4iMAQAA3cKmkRbLhPkCCKOfPnx+fsQZsSlFBPWRxB9BMefgCfUJlyPopexNOfXrYYJdnlAXlWG9xpnGZ9u3fNP4WvOg619nI2P75fnyn2NEAcPA7uovSOH+SvRWEnzOHNSen2tsfBKVteWB5iNO2T2olCS24vycwCynNK6Ej87+j/pTi8n2BXfSUEB2NKAmYvrgobT6oz1BwllZJnuZr2shwrHVdcEY6dF26H1XiWUOAZxMXNjqwGwUgsQ5EKNQNO/ZgJ/y1s3OxOWBMvNE5vvW7U60VoKYJAhCpUCggtPwYag2IHc7/dpd+MsM2iONxF1Y5oC/5OdEKP6yc9y6jDrnB528UFc7I07pWrft2+gpbjlvAJuasZi2rE+FRTLj1nWzSQ6yo1Rz7HiO5s9xagGZ3zypp0894bQB+h6MsnFyTsbncUC2ikoveoHmpDdCR+ZHqxBsd+gbUo2HNt7RJzs2Zn8=',
                    '_abck': 'D02A23857DB99D52D89CB9A4F6B4170E~-1~YAAQF8bOF9cJX4iMAQAAQsOmkQvPnb3gW3R/Ls+KTpvMDkMgq7rbY2wIzTm+vvWNy0bvHKuHtA8uC073Rda/ny0FCorcr5anG+ERrgVy6kl3I4uRPmP7YPB8bzjKmcDUu3wu+fKMQtTkXo73AjAqIUFgMR0edaOnLKmrXRSBnt3ZBBw4zRHH5jiQkE0mn7ZIWf2JqLg4NVr9E+EqaO4fO0lA5AZkGVQromazKkObnI4+18DZwRgyLgncnvCl9KRHleF/OuOAu/wyrkGvonkImlMi45ohb9kRugQf62S6JrPMDxkc/Y74xQYUBWD8IYTujJNLMXq2qAWUw6TyN3c60I7Ua6/qjnJIcP3zBCJkAamEwdEv3zMsPhdqFPhrb3YsdYogmi2Oj7KigJVgCCBuYRdONNNeaKckPMAHDVoIlWrPJIVx3GYxRQ==~-1~-1~-1',
                    'RT': '"z=1&dm=www.target.com.au&si=f62fc03f-e4ae-411c-aed7-3bd9f293a082&ss=lqgnh2eb&sl=0&tt=0"',
                }

        headers = {
                    'authority': 'www.target.com.au',
                    'accept': 'application/json, text/plain, */*',
                    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                    'cache-control': 'no-cache',
                    'pragma': 'no-cache',
                    'referer': 'https://www.target.com.au/p/lego-technic-snow-groomer-42148/67760114',
                    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"macOS"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                }
    
        for productItem in productItemList:

            productUrl = productItem.xpath(".//div[1]/a/@href").get()
            
            productId = "AukingTGP" + productUrl.split("/")[-1]
            productSecondId = productId
            productName = productItem.xpath(".//div[3]/a/p/text()").get()
            productBrand = "Lego"
            productThumbnailImageUrl = productItem.xpath(".//div[1]/a/img/@src").get()

            try:
                productPrice = float(productItem.xpath(".//*[@data-testid='offer-price']/p/text()").get().replace("$", ""))
            except:
                productPrice = float(productItem.xpath(".//*[@data-testid='was-price']/p/text()").get().replace("$", ""))
            
            productPageUrl = productUrl

            if productPrice < 200:
            
                yield scrapy.Request(
                        url=productPageUrl,
                        headers=headers,
                        cookies=cookies,
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
        price = math.ceil(productPrice * 1.1 * 4.8)
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


