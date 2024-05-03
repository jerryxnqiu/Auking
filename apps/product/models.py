from django.db import models
from db.baseModel import BaseModel
from tinymce.models import HTMLField
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models import F, Max, Count, OuterRef, Subquery
import math



# Create your models here.
#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
### Independent, supporting tables
class ProductLogisticsAuExpress(BaseModel):
    """Product Logistics Model, for AuExpress"""

    canBeMixed = (
        (0, 'No'),
        (1, 'Yes'),
    )

    name = models.CharField(max_length=256, verbose_name='物品物流种类名称')
    canBeMixed = models.SmallIntegerField(default=1, choices=canBeMixed, verbose_name='可否混装')
    maxQtyperSkuperParcelStandAlone = models.IntegerField(default=1, verbose_name='单品每包裹最大数量')
    maxQtyperCategoryperParcelStandAlone = models.IntegerField(default=1, verbose_name='同类商品每包裹最大数量')
    maxQtyperParcelMixed = models.IntegerField(default=1, verbose_name='混装每包最大数量')
    extraTax = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='额外税费')
    maxTotalQtyperParcel = models.IntegerField(default=1, verbose_name='包裹物件最大数量')
    maxTotalWeightperParcel = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='包裹最大限重')
    maxTotalValueperParcel = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='包裹最大限值')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='物流服务售价 (含GST)')
    gst = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='消费税GST')
    unit = models.CharField(max_length=20, verbose_name='物流单位')


    class Meta:
        db_table = 'dbProductLogisticsAuExpress'
        verbose_name = '01商品物流分类和费率表(澳邮)'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ProductLogisticsEWE(BaseModel):
    """Product Logistics Model, for EWE"""

    canBeMixed = (
        (0, 'No'),
        (1, 'Yes'),
    )

    name = models.CharField(max_length=256, verbose_name='物品物流种类名称')
    canBeMixed = models.SmallIntegerField(default=1, choices=canBeMixed, verbose_name='可否混装')
    maxQtyperSkuperParcelStandAlone = models.IntegerField(default=1, verbose_name='单品每包裹最大数量')
    maxQtyperCategoryperParcelStandAlone = models.IntegerField(default=1, verbose_name='同类商品每包裹最大数量')
    maxQtyperParcelMixed = models.IntegerField(default=1, verbose_name='混装每包最大数量')
    extraTax = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='额外税费')
    maxTotalQtyperParcel = models.IntegerField(default=1, verbose_name='包裹物件最大数量')
    maxTotalWeightperParcel = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='包裹最大限重')
    maxTotalValueperParcel = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='包裹最大限值')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='物流服务售价 (含GST)')
    gst = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='消费税GST')
    unit = models.CharField(max_length=20, verbose_name='物流单位')


    class Meta:
        db_table = 'dbProductLogisticsEWE'
        verbose_name = '02商品物流分类和费率表(EWE)'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ProductAddOnService(BaseModel):
    """Product Add-on Service Model"""

    name = models.CharField(max_length=20, verbose_name='服务名称')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='服务售价 (含GST)')
    gst = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='消费税GST')
    unit = models.CharField(max_length=10, verbose_name='服务单位')

    class Meta:
        db_table = 'dbProductAddOnService'
        verbose_name = '03商品增值服务费表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ProductFromScrapy(BaseModel):
    """Product model, to store data from scrapy"""
    
    category = models.CharField(max_length=192, verbose_name='商品种类名称')
    subCategory = models.CharField(max_length=192, verbose_name='商品子种类名称')
    spu = models.CharField(max_length=192, verbose_name='商品SPU名称')

    lv1BreadcrumbsName = models.CharField(max_length=192, null=True, verbose_name='商品第1阶导航名')
    lv2BreadcrumbsName = models.CharField(max_length=192, null=True, verbose_name='商品第2阶导航名')
    lv3BreadcrumbsName = models.CharField(max_length=192, null=True, verbose_name='商品第3阶导航名')
    lv4BreadcrumbsName = models.CharField(max_length=192, null=True, verbose_name='商品第4阶导航名')
    lv5BreadcrumbsName = models.CharField(max_length=192, null=True, verbose_name='商品第5阶导航名')

    # Unique key
    sourceName = models.CharField(max_length=192, verbose_name='商品源名称')
    sourceNameAndId = models.CharField(max_length=192, verbose_name='商品源名称与原始编号')

    name = models.CharField(max_length=192, verbose_name='商品名称')
    brand = models.CharField(max_length=96, verbose_name='商品品牌')
    description = HTMLField(blank=True, verbose_name='商品简介')
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品进价')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品售价 (含GST)')
    gst = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='消费税GST')
    unit = models.CharField(max_length=20, verbose_name='商品计价单位')

    imageThumbNail = models.CharField(max_length=255, null=True, verbose_name='商品主缩略图')
    imageProductPage = models.CharField(max_length=3060, null=True, verbose_name='商品主页图片')

    weight = models.CharField(max_length=20, verbose_name='商品重量')

    logisticsCategoryAuExpress = models.ForeignKey('ProductLogisticsAuExpress', verbose_name='商品物流分类和费率表 (澳邮)', on_delete=models.CASCADE)
    logisticsCategoryEWE = models.ForeignKey('ProductLogisticsEWE', verbose_name='商品物流分类和费率表 (EWE)', on_delete=models.CASCADE)


    class Meta:
        db_table = 'dbProductFromScrapy'
        verbose_name = '04商品爬虫源表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
### Dependent tables
class ProductCategory(BaseModel):
    """product Category Model"""

    name = models.CharField(max_length=40, verbose_name='种类名称')
    nameCN = models.CharField(max_length=40, verbose_name='种类中文名称')

    logo = models.ImageField(upload_to='images/productCategory', max_length=255, verbose_name='商品种类图标')
    image = models.ImageField(upload_to='images/productCategory', max_length=255, verbose_name='商品种类图片')
    detail = HTMLField(blank=True, verbose_name='商品种类详情')

    class Meta:
        db_table = 'dbProductCategory'
        verbose_name = '05商品Category表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ProductSubCategory(BaseModel):
    """product Sub-Category Model, one category can have multiple sub-categories"""

    category = models.ForeignKey('ProductCategory', verbose_name='商品种类名称', on_delete=models.CASCADE)
    name = models.CharField(max_length=96, verbose_name='子种类名称')
    nameCN = models.CharField(max_length=96, verbose_name='子种类中文名称')
    ## rich text editor
    detail = HTMLField(blank=True, verbose_name='商品子种类详情')

    class Meta:
        db_table = 'dbProductSubCategory'
        verbose_name = '06商品SubCategory表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ProductSPU(BaseModel):
    """Product SPU Model, standard product unit (SPU) is the smallest unit of commodity information aggregation"""
    
    category = models.ForeignKey('ProductCategory', verbose_name='商品种类名称', on_delete=models.CASCADE)
    subCategory = models.ForeignKey('ProductSubCategory', verbose_name='商品子种类名称', on_delete=models.CASCADE)
    name = models.CharField(max_length=96, verbose_name='商品SPU名称')
    nameCN = models.CharField(max_length=96, verbose_name='商品SPU中文名称')

    ## rich text editor
    detail = HTMLField(blank=True, verbose_name='商品SPU详情')

    class Meta:
        db_table = 'dbProductSPU'
        verbose_name = '07商品SPU表'
        verbose_name_plural = verbose_name
    
    def __str__(self):
        return self.name


class ProductSKU(BaseModel):
    """Product SKU Model, stock keeping unit"""

    status_choice = (
        (0, 'Offline'),
        (1, 'Online'),
    )

    status_onsales = (
        (0, 'Not on sales'),
        (1, 'On sales'),
    )

    category = models.ForeignKey('ProductCategory', verbose_name='商品种类名称', on_delete=models.CASCADE)
    subCategory = models.ForeignKey('ProductSubCategory', verbose_name='商品子种类名称', on_delete=models.CASCADE)
    spu = models.ForeignKey('ProductSPU', verbose_name='商品SPU名称', on_delete=models.CASCADE)

    # Unique key
    sourceNameAndId = models.CharField(max_length=192, verbose_name='商品源名称与原始编号')
    name = models.CharField(max_length=192, verbose_name='商品名称')
    nameCN = models.CharField(max_length=192, verbose_name='商品中文名称')

    brand = models.CharField(max_length=96, verbose_name='商品品牌')
    description = HTMLField(blank=True, verbose_name='商品简介')
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品进价')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='商品售价 (含GST)')
    gst = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='消费税GST')
    unit = models.CharField(max_length=20, verbose_name='商品计价单位')

    image = models.ImageField(upload_to='images/productSKU', max_length=255, verbose_name='商品主缩略图')

    weight = models.CharField(max_length=20, verbose_name='商品重量')
    stock = models.IntegerField(default=1, verbose_name='商品库存')
    sales = models.IntegerField(default=0, verbose_name='商品销量')

    logisticsCategoryAuExpress = models.ForeignKey('ProductLogisticsAuExpress', verbose_name='商品物流分类和费率表 (澳邮)', on_delete=models.CASCADE)
    logisticsCategoryEWE = models.ForeignKey('ProductLogisticsEWE', verbose_name='商品物流分类和费率表 (EWE)', on_delete=models.CASCADE)

    onsales = models.SmallIntegerField(default=1, choices=status_onsales, verbose_name='商品是否促销')
    status = models.SmallIntegerField(default=1, choices=status_choice, verbose_name='商品状态')

    class Meta:
        db_table = 'dbProductSKU'
        verbose_name = '08商品SKU表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ProductImage(BaseModel):
    """Product Image Model, images used in product main page"""

    sku = models.ForeignKey('ProductSKU', verbose_name='商品SKU', on_delete=models.CASCADE)

    image = models.ImageField(upload_to='images/productSKU', max_length=255, verbose_name='商品主页图片')

    class Meta:
        db_table = 'dbProductImage'
        verbose_name = '09商品图片表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sku.name


#######################################################################################################################
#######################################################################################################################
#######################################################################################################################
### Marking Related tables
class IndexProductBanner(BaseModel):
    """Homepage Product Banner Model, one line per advertising picture (size: xxxx x xxxx)"""

    name = models.CharField(max_length=256, verbose_name='轮播产品图片名称')
    image = models.ImageField(upload_to='images/productBanner', max_length=255, verbose_name='轮播产品图片')

    index = models.SmallIntegerField(default=0, verbose_name='轮播顺序')

    class Meta:
        db_table = 'dbIndexProductBanner'
        verbose_name = '10首页轮播商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class IndexPromotionBanner(BaseModel):
    """Homepage Promotion Banner, one line one activity"""

    name = models.CharField(max_length=20, verbose_name='活动名称')
    url = models.CharField(max_length=256, verbose_name='活动链接')

    image = models.ImageField(upload_to='images/promotionBanner', max_length=255, verbose_name='活动图片')
    discount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='活动促销折扣')
    
    index = models.SmallIntegerField(default=0, verbose_name='活动展示顺序')

    class Meta:
        db_table = 'dbIndexPromotionBanner'
        verbose_name = "11主页促销活动规划表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class IndexCategoryProductBanner(BaseModel):
    """Homepage Product Display per Category, to display what will be on the Homepage, either by text, or the image"""

    DISPLAY_CATEGORY_CHOICES = (
        (0, "title"),
        (1, "image")
    )

    category = models.ForeignKey('ProductCategory', verbose_name='商品种类名称', on_delete=models.CASCADE)
    subCategory = models.ForeignKey('ProductSubCategory', verbose_name='商品子种类名称', on_delete=models.CASCADE)
    spu = models.ForeignKey('ProductSPU', verbose_name='商品SPU名称', on_delete=models.CASCADE)
    sku = models.ForeignKey('ProductSKU', verbose_name='商品SKU', on_delete=models.CASCADE)
    
    displayCategory = models.SmallIntegerField(default=1, choices=DISPLAY_CATEGORY_CHOICES, verbose_name='展示类型')
    index = models.SmallIntegerField(default=0, verbose_name='展示顺序')

    class Meta:
        db_table = 'dbIndexCategoryProductBanner'
        verbose_name = "12主页分类展示商品规划表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sku.name


class BulkPurchaseDiscount(BaseModel):
    """Product Bulk Purchase Discount Model, to apply per sub-category"""

    category = models.ForeignKey('ProductCategory', verbose_name='商品种类名称', on_delete=models.CASCADE)
    subCategory = models.ForeignKey('ProductSubCategory', verbose_name='商品子种类名称', on_delete=models.CASCADE)

    ## progressively increasing discount, stop at "stopQuantity"
    stopQuantity = models.CharField(max_length=20, verbose_name='折扣停用数量')
    progressiveDiscount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='递进折扣')

    class Meta:
        db_table = 'dbBulkPurchaseDiscount'
        verbose_name = "13产品折扣规划表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.subCategory.name


@receiver(post_save, sender=ProductFromScrapy)
def updateProductSubCategory(sender, instance, **kwargs):

    categoryValue = instance.category
    subCategoryValue = instance.subCategory

    # To check if the value exists
    existingProductSubCategoryInstance = ProductSubCategory.objects.filter(name=subCategoryValue).first()

    if existingProductSubCategoryInstance:
        # If the value exists, update the fieldB value
        existingProductSubCategoryInstance.category = ProductCategory.objects.get(name=categoryValue)
        existingProductSubCategoryInstance.name = subCategoryValue
        existingProductSubCategoryInstance.nameCN = subCategoryValue
        existingProductSubCategoryInstance.save()
    else:
        # If the value doesn't exist, create a new Model1B instance
        newProductSubCategoryInstance = ProductSubCategory(category=ProductCategory.objects.get(name=categoryValue),
                                                           name=subCategoryValue, 
                                                           nameCN=subCategoryValue)
        newProductSubCategoryInstance.save()

@receiver(post_save, sender=ProductFromScrapy)
def updateProductSPU(sender, instance, **kwargs):

    categoryValue = instance.category
    subCategoryValue = instance.subCategory
    spuValue = instance.spu

    # To check if the value exists
    existingProductSPUInstance = ProductSPU.objects.filter(name=spuValue).first()

    if existingProductSPUInstance:
        # If the value exists, update the fieldB value
        existingProductSPUInstance.category = ProductCategory.objects.get(name=categoryValue)
        existingProductSPUInstance.subCategory = ProductSubCategory.objects.get(name=subCategoryValue)
        existingProductSPUInstance.name = spuValue
        existingProductSPUInstance.nameCN = spuValue
        existingProductSPUInstance.save()
    else:
        # If the value doesn't exist, create a new Model1B instance
        newProductSPUInstance = ProductSPU(category=ProductCategory.objects.get(name=categoryValue),
                                           subCategory=ProductSubCategory.objects.get(name=subCategoryValue),
                                           name=spuValue, 
                                           nameCN=spuValue)
        newProductSPUInstance.save()

@receiver(post_save, sender=ProductFromScrapy)
def updateProductSKU(sender, instance, **kwargs):

    categoryValue = instance.category
    subCategoryValue = instance.subCategory
    spuValue = instance.spu

    sourceNameAndIdValue = instance.sourceNameAndId
    nameValue = instance.name

    brandValue = instance.brand
    descriptionValue = instance.description
    costValue = instance.cost
    priceValue = instance.price
    gstValue = instance.gst
    unitValue = instance.unit

    imageThumbNailValue = instance.imageThumbNail
    weightValue = instance.weight
    logisticsCategoryAuExpressValue = instance.logisticsCategoryAuExpress
    logisticsCategoryEWEValue = instance.logisticsCategoryEWE

    # To check if the value exists
    existingProductSKUInstance = ProductSKU.objects.filter(sourceNameAndId=sourceNameAndIdValue).first()

    if existingProductSKUInstance:
        # If the value exists, update the fieldB value
        existingProductSKUInstance.category = ProductCategory.objects.get(name=categoryValue)
        existingProductSKUInstance.subCategory = ProductSubCategory.objects.get(name=subCategoryValue)
        existingProductSKUInstance.spu = ProductSPU.objects.get(name=spuValue)

        existingProductSKUInstance.name = nameValue
        existingProductSKUInstance.nameCN = nameValue
        existingProductSKUInstance.brand = brandValue
        existingProductSKUInstance.description = descriptionValue
        existingProductSKUInstance.cost = costValue
        existingProductSKUInstance.price = priceValue
        existingProductSKUInstance.gst = gstValue

        existingProductSKUInstance.image = imageThumbNailValue
        existingProductSKUInstance.weight = weightValue

        existingProductSKUInstance.logisticsCategoryAuExpress = logisticsCategoryAuExpressValue
        existingProductSKUInstance.logisticsCategoryEWE = logisticsCategoryEWEValue
        existingProductSKUInstance.save()

    else:
        # If the value doesn't exist, create a new Model1B instance
        newProductSKUInstance = ProductSKU(category=ProductCategory.objects.get(name=categoryValue),
                                           subCategory=ProductSubCategory.objects.get(name=subCategoryValue),
                                           spu=ProductSPU.objects.get(name=spuValue),
                                           sourceNameAndId=sourceNameAndIdValue,
                                           name=nameValue, 
                                           nameCN=nameValue,
                                           brand=brandValue,
                                           description=descriptionValue,
                                           cost=costValue,
                                           price=priceValue,
                                           gst=gstValue,
                                           unit=unitValue,
                                           image=imageThumbNailValue,
                                           weight=weightValue,
                                           stock=2000,
                                           sales=0,
                                           logisticsCategoryAuExpress=logisticsCategoryAuExpressValue,
                                           logisticsCategoryEWE=logisticsCategoryEWEValue,
                                           onsales=0,
                                           status=1)
        newProductSKUInstance.save()

@receiver(post_save, sender=ProductFromScrapy)
def updateProductImage(sender, instance, **kwargs):

    nameValue = instance.name
    imageProductPageValueList = instance.imageProductPage

    for imageProductPageValue in imageProductPageValueList:

        # To check if the value exists
        existingProductImageInstance = ProductImage.objects.filter(image=imageProductPageValue).first()

        if existingProductImageInstance:
            # If the value exists, update the fieldB value
            existingProductImageInstance.sku = ProductSKU.objects.get(name=nameValue)
            existingProductImageInstance.image = imageProductPageValue
            existingProductImageInstance.save()
        else:
            # If the value doesn't exist, create a new Model1B instance
            newProductImageInstance = ProductImage(sku=ProductSKU.objects.get(name=nameValue),
                                                   image=imageProductPageValue)
            newProductImageInstance.save()


def updateIndexCategoryProductBanner():
    
    # To clear the old records before adding new ones
    IndexCategoryProductBanner.objects.all().delete()

    # To get the max sales item in "category" and "subcategory" from "ProductSKU" table
    categories = ProductSKU.objects.values('category').annotate(
        numOfSubcategories=Count('subCategory', distinct=True)
    )

    for categoryData in categories:
        category = categoryData['category']
        numOfSubcategories = categoryData['numOfSubcategories']
        
        if numOfSubcategories < 14:
            
            # To select multiple top sales items from each subcategory to fill the 14 slots
            subcategories = ProductSKU.objects.filter(
                category=category
            ).values('subCategory').annotate(
                sales=Max('sales')
            ).order_by('-sales')
            
            # To calculate the max list index for the subCategory lists, 
            # e.g.: as numOfSubcategories < 14, each subCategory has equal quantity of items to be selected, 
            # only in the last round, sales quantity larger will be rank higher
            indexKeep = math.floor(14 / len(subcategories))

            itemList = []
            for subcategory in subcategories:
                subcategoryName = subcategory['subCategory']
                
                topItems = ProductSKU.objects.filter(
                    category=category,
                    subCategory=subcategoryName,
                    sales=subcategory['sales']
                ).order_by('-sales')[:indexKeep]

                itemList += list(topItems)

            # If itemList is not enough of 14, to fill up the slots by the highest sales item
            # from the remaining list
            if len(itemList) < 14:

                remainingItems = ProductSKU.objects.filter(
                    category=category
                ).exclude(
                    id__in=[item.id for item in itemList]
                ).order_by('-sales')[:(14-len(itemList))]
    
                itemList += list(remainingItems)
                
            # To update the "IndexCategoryProductBanner" table
            # Rules are:
            # 1. 1 - 10, set to "image",
            # 2. 11 - 14, set to "title"
            
            itemIndex = 0
            imageOrTitle = "image"
            itemList = sorted(itemList, key=lambda x: x.sales, reverse=True)
            for item in itemList:
                
                if imageOrTitle == "image":
                    displayCategory = 1
                else:
                    displayCategory = 0

                if itemIndex == 10:
                    itemIndex = 0
                    imageOrTitle = "title"
                    displayCategory = 0

                indexCategoryProductBannerinstance, _ = IndexCategoryProductBanner.objects.get_or_create(
                    category=ProductCategory.objects.get(name=ProductSKU.objects.get(name=item).category),
                    subCategory=ProductSubCategory.objects.get(name=ProductSKU.objects.get(name=item).subCategory),
                    spu=ProductSPU.objects.get(name=ProductSKU.objects.get(name=item).spu),
                    sku=ProductSKU.objects.get(name=item),
                    displayCategory=displayCategory,
                    index=itemIndex,
                )
                indexCategoryProductBannerinstance.save()
                print(displayCategory)
                itemIndex += 1

        else:

            # To select the top sales items from each subcategory to fill the 14 slots
            subcategories = ProductSKU.objects.filter(
                category=category
            ).values('subCategory').annotate(
                sales=Max('sales')
            ).order_by('-sales')


            itemList = []
            for subcategory in subcategories:
                subcategoryName = subcategory['subCategory']
                
                topItem = ProductSKU.objects.filter(
                    category=category,
                    subCategory=subcategoryName,
                    sales=subcategory['sales']
                ).order_by('-sales')[0]

                itemList.append(topItem)

            # To update the "IndexCategoryProductBanner" table
            # Rules are:
            # 1. 1 - 10, set to "image",
            # 2. 11 - 14, set to "title"
            
            itemIndex = 0
            imageOrTitle = "image"
            itemList = sorted(itemList, key=lambda x: x.sales, reverse=True)
            itemList = itemList[:14]

            for item in itemList:
                
                if imageOrTitle == "image":
                    displayCategory = 1
                else:
                    displayCategory = 0

                if itemIndex == 10:
                    itemIndex = 0
                    imageOrTitle = "title"
                    displayCategory = 0

                indexCategoryProductBannerinstance, _ = IndexCategoryProductBanner.objects.get_or_create(
                    category=ProductCategory.objects.get(name=ProductSKU.objects.get(name=item).category),
                    subCategory=ProductSubCategory.objects.get(name=ProductSKU.objects.get(name=item).subCategory),
                    spu=ProductSPU.objects.get(name=ProductSKU.objects.get(name=item).spu),
                    sku=ProductSKU.objects.get(name=item),
                    displayCategory=displayCategory,
                    index=itemIndex,
                )
                indexCategoryProductBannerinstance.save()
                print(displayCategory)
                itemIndex += 1
