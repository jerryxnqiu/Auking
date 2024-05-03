from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django_redis import get_redis_connection
from bocfx import bocfx
import math

from product.models import ProductCategory, ProductSKU, ProductAddOnService
from utils.mixin import LoginRequiredMixin

### Global variable for RMB to AUD exchange rate
audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000

### Create your views here.
### To delete a record in the shopping cart
class CartDeleteView(View):
    """To delete the record in shopping cart"""
    
    def post(self, request):

        ### 1. Receiving data #####################################################################
        # To get the user information
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        skuIdandAddOnServiceIds = request.POST.get('skuIdandAddOnServiceIds')
        
        # Get the first part as the skuId
        skuId = skuIdandAddOnServiceIds.split("_")[0]
        
        ### 2. Checking data ######################################################################
        if not skuId:
            return JsonResponse({'res': 1, 'errmsg': '无效的商品id'})

        try:
            sku = ProductSKU.objects.get(id=skuId)
        except ProductSKU.DoesNotExist as e:
            return JsonResponse({'res': 2, 'errmsg': '商品待补充'})

        ### 3. Processing data ####################################################################
        # To update the product quantity in shopping cart
        conn = get_redis_connection('default')
        cartKey = 'cart_%d' % user.id

        # Removes the specified fields from the hash stored at key. 
        # Specified fields that do not exist within this hash are ignored. 
        # If key does not exist, it is treated as an empty hash and this command returns 0.
        conn.hdel(cartKey, skuIdandAddOnServiceIds)

        # return the response
        return JsonResponse({'res': 3, 'message': '删除成功'})


### To update the shopping cart
class CartUpdateView(View):
    """To update the product quantity in shopping cart"""
    
    def post(self, request):
        ### 1. Receiving data #####################################################################
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        skuIdandAddOnServiceIds = request.POST.get('skuIdandAddOnServiceIds')
        count = request.POST.get('count')

        # Get the first part as the skuId
        skuId = skuIdandAddOnServiceIds.split("_")[0]


        ### 2. Checking data ######################################################################s
        if not all([skuId, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 2, 'errmsg': '商品数目格式错误'})

        try:
            sku = ProductSKU.objects.get(id=skuId)
        except ProductSKU.DoesNotExist as e:
            return JsonResponse({'res': 3, 'errmsg': '商品待补充'})


        ### 3. Processing data ####################################################################
        # To update the product quantity in shopping cart
        conn = get_redis_connection('default')
        cartKey = 'cart_%d' % user.id

        # To check if product still has stock
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})

        # If skuIdandAddOnServiceIds (skuId + addOnServiceIds) exists, update the quantity, or create new one
        # Returns the value associated with field in the hash stored at key.
        conn.hset(cartKey, skuIdandAddOnServiceIds, count)

        # return the response
        return JsonResponse({'res': 5, 'errmsg': '更新成功'})


### To increase quantity in a shopping cart
class CartAddView(View):
    """Shopping Cart Addition Record"""

    def post(self, request):
        ### 1. Receiving data #####################################################################
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        skuIdandAddOnServiceIds = request.POST.get('skuIdandAddOnServiceIds')
        count = request.POST.get('count')

        # Get the first part as the skuId
        skuId = skuIdandAddOnServiceIds.split("_")[0]


        ### 2. Checking data ######################################################################
        if not all([skuIdandAddOnServiceIds, count]):
            return JsonResponse({'res': 1, 'errmsg': '数据不完整'})

        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 2, 'errmsg': '商品数目格式错误'})

        try:
            sku = ProductSKU.objects.get(id=skuId)
        except ProductSKU.DoesNotExist as e:
            return JsonResponse({'res': 3, 'errmsg': '商品待补充'})


        ### 3. Processing data ####################################################################
        # To add into the shopping cart, 
        # redis is using the hash format to store the shopping cart information，
        # cart_userId: {'42_1_3': 3, '52_2_3_4': 5} 
        # use "hget" to get the product quantity from keys, e.g."cart_userId, skuId"
        conn = get_redis_connection('default')
        cartKey = 'cart_%d' % user.id

        # If no such product associated with the key, return null or false
        cartCount = conn.hget(cartKey, skuIdandAddOnServiceIds)
        if cartCount:
            count += int(cartCount)

        # If skuIdandAddOnServiceIds (skuId + addOnServiceIds) exists, update the quantity, or create new one
        # Returns the value associated with field in the hash stored at key.
        conn.hset(cartKey, skuIdandAddOnServiceIds, count)

        # To check if product still has stock
        if count > sku.stock:
            return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})

        # To get the product quantity inside the shopping cart
        totalCount = conn.hlen(cartKey)

        # return the response
        return JsonResponse({'res': 5, 'totalCount': totalCount, 'errmsg': '添加成功'})


### To show shopping cart
class CartInfoView(LoginRequiredMixin, View):
    # Shopping cart info summary page

    def get(self, request):

        ### 1. Receiving data #####################################################################
        user = request.user

        # To get the shopping cart information from redis
        conn = get_redis_connection('default')
        cartKey = 'cart_%s' % user.id
        cartDict = conn.hgetall(cartKey)

        skus = []
        totalCount = 0
        totalPrice = 0
        totalPriceCN = 0

        for skuIdandAddOnServiceIds, count in cartDict.items():
            
            # To get the product information from product ID
            skuIdandAddOnServiceIds = skuIdandAddOnServiceIds.decode()
            count = int(count.decode())
            skuId = skuIdandAddOnServiceIds.split("_")[0]
            addOnServicesIds = skuIdandAddOnServiceIds.split("_")[1:]

            # To get the sku and addOnService
            sku = ProductSKU.objects.get(id=skuId)

            addOnServices = []
            for addOnServicesId in addOnServicesIds:
                addOnService = ProductAddOnService.objects.get(id=addOnServicesId)
                addOnServices.append(addOnService)

            # To update the sku price with live exchange rate, 4.8 is the initial exchange rate used in Scrapy for database ingestion
            sku.price = math.ceil(float(sku.price) / 4.8 * 10) / 10
            sku.priceCN = math.ceil(float(sku.price) * audExRate *10) / 10

            # To get the product price
            amount = sku.price * int(count)
            amountCN = sku.priceCN * int(count)
            
            # To add values to "sku" object dynamically
            sku.amount = round(amount, 1)
            sku.amountCN = round(amountCN, 1)
            sku.count = count
            sku.skuIdandAddOnServiceIds = skuIdandAddOnServiceIds
            sku.addOnServices = addOnServices           # To pass the add-on service name inside each line item
            sku.addOnServicesIds = addOnServicesIds     # To pass the add-on service ID to facilitate parameter passing to jQuery
            
            # To append to the list
            skus.append(sku)

            totalCount += count
            totalPrice += amount
            totalPriceCN += amountCN

        
        # To get the product category
        categories = ProductCategory.objects.all()
        totalPrice = math.ceil(totalPrice * 10) / 10
        totalPriceCN = round(totalPriceCN, 1)


        # To summarize the response 
        context = {
            'audExRate': audExRate,
            'categories': categories,
            'skus': skus,
            'totalCount': totalCount,
            'totalPrice': totalPrice,
            'totalPriceCN': totalPriceCN,
        }

        return render(request, 'cart.html', context)