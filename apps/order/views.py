from typing import Any
import stripe
from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse, HttpResponse
from django.db import transaction
from django.db.models import Sum
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from utils.mixin import LoginRequiredMixin
from django.urls import reverse
from django_redis import get_redis_connection

from django.conf import settings
import pandas as pd
import math
import hashlib
from urllib.parse import urlencode, quote
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from celery_tasks.tasks import sendPaymentSuccessEmail, sendWeChatPaynentFailureEmail
from bocfx import bocfx
import math
import os
from dotenv import load_dotenv
import requests
import boto3

from order.models import OrderInfo, OrderProduct, OrderProductandServiceMapping, OrderTracking
from product.models import ProductCategory, ProductSKU, ProductAddOnService, ProductLogisticsAuExpress, ProductLogisticsEWE
from user.models import SenderAddress, ReceiverAddress


### Global variable for RMB to AUD exchange rate
audExRate = math.ceil(float(bocfx('AUD','SE,ASK')[0]) * 100) / 10000


### Create your views here.
### To calculate the parcel arrangement for products, and send to the "order place" page, from "cart.html"
class OrderPlaceView(LoginRequiredMixin, View):
    """Order Placing Page"""

    ###################################################################################################################
    ###################################################################################################################
    # For parcel with "Cannot be Mixed" products, return new parcelId
    def parcelIdIncrementCannotBeMixed(self,
                                       parcelTable,
                                       parcelIdSet,
                                       parcelId,
                                       logisticsCategoryNameHash,
                                       canBeMixed,
                                       skuMaxQtyperCategoryperParcelStandAlone):
        
        # To construct the temp dataframe for parcel packaing analysis
        parcelTable = pd.DataFrame(parcelTable, 
                                   columns=['parcel Id',
                                            'sku Id',
                                            'count In Parcel',
                                            'sku Weight',
                                            'sku and Add-On Service ID List',
                                            'sku Name',
                                            'sku Price',
                                            'logistics Category Name',
                                            'logistics Category Name Hash',
                                            'can Be Mixed',
                                            'max Qty per Sku per Parcel StandAlone',
                                            'max Qty per Category per Parcel StandAlone',
                                            'max Qty per Parcel Mixed',
                                            'extra Tax',
                                            'max Total Qty per Parcel',
                                            'max Total Weight per Parcel',
                                            'max Total Value per Parcel',
                                            'logistics Price per Unit',
                                            'logistics Price Gst'])
        

        ###########################################################################################
        # To select the dataframe of current "canBeMixed" status
        parcelTableCurrentStatusParcel = parcelTable[parcelTable['can Be Mixed'] == canBeMixed]

        # To check if more products can be fit into the existing parcelId 
        for parcelIdkey in parcelIdSet:

            temp = parcelTableCurrentStatusParcel[parcelTableCurrentStatusParcel['parcel Id'] == parcelIdkey]
        
            # If any parcel box condition fulfilled, use the parcel box ID for the incumbent product
            # 1. "Cannot be mixed" + new "logistics category" is same 
            # 2. "Cannot be mixed" + "Parcel contains product quantity within allowance limit"
            if (temp.iloc[0]['logistics Category Name Hash'] == logisticsCategoryNameHash) & \
               (temp.shape[0] < skuMaxQtyperCategoryperParcelStandAlone):

                return parcelId

        return parcelId + 1


    ###################################################################################################################
    ###################################################################################################################
    # For parcel with "Can be Mixed" products, return new parcelId
    def parcelIdIncrementCanBeMixed(self,
                                    parcelTable,
                                    skuId,
                                    parcelIdSet,
                                    parcelId,
                                    logisticsCategoryNameHash,
                                    canBeMixed,
                                    skuMaxQtyperSkuperParcelStandAlone,
                                    skuMaxQtyperParcelMixed,
                                    skuMaxTotalQtyperParcel,
                                    skuMaxTotalWeightperParcel,
                                    skuMaxTotalValueperParcel):

        # To construct the temp dataframe for parcel packaing analysis
        parcelTable = pd.DataFrame(parcelTable, 
                                   columns=['parcel Id',
                                            'sku Id',
                                            'count In Parcel',
                                            'sku Weight',
                                            'sku and Add-On Service ID List',
                                            'sku Name',
                                            'sku Price',
                                            'logistics Category Name',
                                            'logistics Category Name Hash',
                                            'can Be Mixed',
                                            'max Qty per Sku per Parcel StandAlone',
                                            'max Qty per Category per Parcel StandAlone',
                                            'max Qty per Parcel Mixed',
                                            'extra Tax',
                                            'max Total Qty per Parcel',
                                            'max Total Weight per Parcel',
                                            'max Total Value per Parcel',
                                            'logistics Price per Unit',
                                            'logistics Price Gst'])


        ###########################################################################################
        # To select the dataframe of current "canBeMixed" status
        parcelTableCurrentStatusParcel = parcelTable[parcelTable['can Be Mixed'] == canBeMixed]
        
        # To keep the parcelId in the set if they are in the current "canBeMixed" dataframe
        parcelIdSet.intersection_update(list(parcelTableCurrentStatusParcel["parcel Id"]))

        # To check if more products can be fit into the existing parcelId 
        for parcelIdkey in parcelIdSet:

            temp = parcelTableCurrentStatusParcel[parcelTableCurrentStatusParcel['parcel Id'] == parcelIdkey]

            # If any parcel box condition fulfilled, use the parcel box ID for the incumbent product
            # sku Price is in RMB, skuMaxTotalValueperParcel is in AUD and exchange rate uses fix rate 4.8
            if ((temp['sku Price'].astype(float).sum() / 4.8) < skuMaxTotalValueperParcel) & \
               (temp['sku Weight'].astype(float).sum() < skuMaxTotalWeightperParcel) & \
               (temp.shape[0] <= skuMaxTotalQtyperParcel) & \
               ((temp['logistics Category Name Hash'].drop_duplicates().shape[0] > 1) & 
                (temp[temp['logistics Category Name Hash'] == logisticsCategoryNameHash].shape[0]) < skuMaxQtyperParcelMixed) & \
               (temp[temp['sku Id'] == skuId].shape[0] < skuMaxQtyperSkuperParcelStandAlone):

                return parcelIdkey

        # If all parcel box condition not fulfilled
        return parcelId + 1


    ###################################################################################################################
    ###################################################################################################################
    # To get the content from "cart.html"
    def post(self, request):
        
        ###########################################################################################
        ### 1. Getting data #######################################################################
        # To get the user information
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '请先登录'})

        # To get the product category
        categories = ProductCategory.objects.all()

        # To get the product Ids submitted
        skuIdandAddOnServiceIdsList = request.POST.getlist('skuIdandAddOnServiceIds')

        # To get the product Ids and save as list
        skuIds = []
        for skuIdandAddOnServiceIds in skuIdandAddOnServiceIdsList:
            skuIds.append(skuIdandAddOnServiceIds.split("_")[0])

        # To verify if there is product Id
        if not skuIds:
            return redirect(reverse('cart:show'))

        conn = get_redis_connection('default')
        cartKey = 'cart_%s' % user.id


        ###########################################################################################
        ### 2. Checking data ######################################################################
        # To check if user sending and receiving address exists, if not, redirect to user center pages
        try:
            receiverAddresses = ReceiverAddress.objects.filter(user=user)
            receiverAddressDefault = ReceiverAddress.objects.get(user=user, isDefault=True)
        except:
            return redirect(reverse('user:receiverAddress'))

        try:
            senderAddresses = SenderAddress.objects.filter(user=user)
            senderAddressDefault = SenderAddress.objects.get(user=user, isDefault=True)
        except:
            return redirect(reverse('user:senderAddress'))


        ###########################################################################################
        ### 3. Processing data ####################################################################
        # To populate logistics information for each product
        # To initialize variables
        parcelAuExpress = []
        parcelEWE = []
        addOnServices = []
        skuCountList = []

        # To prepare the dataframe
        for skuIdandAddOnServiceIds in skuIdandAddOnServiceIdsList:
            
            # To get product ID and quantity
            skuId = skuIdandAddOnServiceIds.split("_")[0]
            sku = ProductSKU.objects.get(id=skuId)
            skuWeight = sku.weight
            skuCount = int(conn.hget(cartKey, skuIdandAddOnServiceIds))

            # To get sku count list
            skuCountList.append(skuCount)

            # To get add-on service, price and quantity, to construct add-on service dataframe
            addOnServicesIds = skuIdandAddOnServiceIds.split("_")[1:]
            for addOnServiceId in addOnServicesIds:
                
                addOnService = ProductAddOnService.objects.get(id=addOnServiceId)
                addOnServicePrice = addOnService.price
                addOnServiceGst = addOnService.gst
                addOnServiceSubtotal = addOnServicePrice * skuCount

                addOnServices.append([addOnServiceId,
                                      addOnService,
                                      addOnServicePrice,
                                      addOnServiceGst,
                                      skuCount,
                                      addOnServiceSubtotal])

            #######################################################################################
            # To construct AuExpress dataframe
            logisticsCatNameAuExpress = sku.logisticsCategoryAuExpress

            # To convert to hash to avoid special text within the logistics name
            logisticsCatNameHashAuExpress = hashlib.sha256(str(logisticsCatNameAuExpress).encode("utf-8")).hexdigest()

            logisticsAuExpress = ProductLogisticsAuExpress.objects.get(name=sku.logisticsCategoryAuExpress)
            canBeMixedAuExpress = logisticsAuExpress.canBeMixed
            maxQtyperSkuperParcelStandAloneAuExpress = logisticsAuExpress.maxQtyperSkuperParcelStandAlone
            maxQtyperCategoryperParcelStandAloneAuExpress = logisticsAuExpress.maxQtyperCategoryperParcelStandAlone
            maxQtyperParcelMixedAuExpress = logisticsAuExpress.maxQtyperParcelMixed
            extraTaxAuExpress = logisticsAuExpress.extraTax
            maxTotalQtyperParcelAuExpress = logisticsAuExpress.maxTotalQtyperParcel
            maxTotalWeightperParcelAuExpress = logisticsAuExpress.maxTotalWeightperParcel
            maxTotalValueperParcelAuExpress = logisticsAuExpress.maxTotalValueperParcel
            logisticsPriceAuExpress = logisticsAuExpress.price
            logisticsPriceGstAuExpress = logisticsAuExpress.gst
            logisticsPriceUnitAuExpress = logisticsAuExpress.unit
            subTotalWeightAuExpress = skuCount * float(skuWeight)

            parcelAuExpress.append([skuId,
                                    skuCount,
                                    skuWeight,
                                    skuIdandAddOnServiceIds,
                                    logisticsCatNameAuExpress,
                                    logisticsCatNameHashAuExpress,
                                    canBeMixedAuExpress,
                                    maxQtyperSkuperParcelStandAloneAuExpress,
                                    maxQtyperCategoryperParcelStandAloneAuExpress,
                                    maxQtyperParcelMixedAuExpress,
                                    extraTaxAuExpress,
                                    maxTotalQtyperParcelAuExpress,
                                    maxTotalWeightperParcelAuExpress,
                                    maxTotalValueperParcelAuExpress,
                                    logisticsPriceAuExpress,
                                    logisticsPriceGstAuExpress,
                                    logisticsPriceUnitAuExpress.encode("utf-8").strip().decode("utf-8"),
                                    subTotalWeightAuExpress])

            #######################################################################################
            # To construct EWE dataframe
            logisticsCatNameEWE = sku.logisticsCategoryEWE

            # To convert to hash to avoid special text within the logistics name
            logisticsCatNameHashEWE = hashlib.sha256(str(logisticsCatNameEWE).encode("utf-8")).hexdigest()

            logisticsEWE = ProductLogisticsEWE.objects.get(name=sku.logisticsCategoryEWE)
            canBeMixedEWE = logisticsEWE.canBeMixed
            maxQtyperSkuperParcelStandAloneEWE	= logisticsEWE.maxQtyperSkuperParcelStandAlone
            maxQtyperCategoryperParcelStandAloneEWE = logisticsEWE.maxQtyperCategoryperParcelStandAlone
            maxQtyperParcelMixedEWE = logisticsEWE.maxQtyperParcelMixed
            extraTaxEWE = logisticsEWE.extraTax
            maxTotalQtyperParcelEWE = logisticsEWE.maxTotalQtyperParcel
            maxTotalWeightperParcelEWE = logisticsEWE.maxTotalWeightperParcel
            maxTotalValueperParcelEWE = logisticsEWE.maxTotalValueperParcel
            logisticsPriceEWE = logisticsEWE.price
            logisticsPriceGstEWE = logisticsEWE.gst
            logisticsPriceUnitEWE = logisticsEWE.unit
            subTotalWeightEWE = skuCount * float(skuWeight)

            parcelEWE.append([skuId,
                              skuCount,
                              skuWeight,
                              skuIdandAddOnServiceIds,
                              logisticsCatNameEWE,
                              logisticsCatNameHashEWE,
                              canBeMixedEWE,
                              maxQtyperSkuperParcelStandAloneEWE,
                              maxQtyperCategoryperParcelStandAloneEWE,
                              maxQtyperParcelMixedEWE,
                              extraTaxEWE,
                              maxTotalQtyperParcelEWE,
                              maxTotalWeightperParcelEWE,
                              maxTotalValueperParcelEWE,
                              logisticsPriceEWE,
                              logisticsPriceGstEWE,
                              logisticsPriceUnitEWE.encode("utf-8").strip().decode("utf-8"),
                              subTotalWeightEWE])

        # To construct the dataframe
        parcelAuExpress = pd.DataFrame(parcelAuExpress, 
                                       columns=['sku Id',
                                                'sku Count',
                                                'sku Weight',
                                                'sku and Add-On Service ID List',
                                                'logistics Category Name',
                                                'logistics Category Name Hash',
                                                'can Be Mixed',
                                                'max Qty per Sku per Parcel StandAlone',
                                                'max Qty per Category per Parcel StandAlone',
                                                'max Qty per Parcel Mixed',
                                                'extra Tax',
                                                'max Total Qty per Parcel',
                                                'max Total Weight per Parcel',
                                                'max Total Value per Parcel',
                                                'logistics Price per Unit',
                                                'logistics Price Gst',
                                                'logistics Price Unit',
                                                'subtotal Weight'])

        parcelEWE = pd.DataFrame(parcelEWE, 
                                 columns=['sku Id',
                                          'sku Count',
                                          'sku Weight',
                                          'sku and Add-On Service ID List',
                                          'logistics Category Name',
                                          'logistics Category Name Hash',
                                          'can Be Mixed',
                                          'max Qty per Sku per Parcel StandAlone',
                                          'max Qty per Category per Parcel StandAlone',
                                          'max Qty per Parcel Mixed',
                                          'extra Tax',
                                          'max Total Qty per Parcel',
                                          'max Total Weight per Parcel',
                                          'max Total Value per Parcel',
                                          'logistics Price per Unit',
                                          'logistics Price Gst',
                                          'logistics Price Unit',
                                          'subtotal Weight'])

        addOnServices = pd.DataFrame(addOnServices, 
                                     columns=['add-On Service Id',
                                              'add-On Service',
                                              'add-On Service Price',
                                              'add-On Service Gst',
                                              'add-On Service Count',
                                              'add-On Service Subtotal'])

        # To calculate key output values
        totalServiceQty = addOnServices["add-On Service Count"].sum()
        totalServicePrice = math.ceil(addOnServices["add-On Service Subtotal"].sum() * 10) / 10
        totalServicePriceCN = math.ceil(float(totalServicePrice) * audExRate * 10) / 10
        totalLogisticsWeight = math.ceil(parcelAuExpress["subtotal Weight"].sum() * 10) / 10


        ###########################################################################################
        ###########################################################################################
        ###########################################################################################
        ### 4. Preparing parcel packaging #########################################################


        ###########################################################################################
        ###########################################################################################
        # To assign parcel ID for each product - AuExpress
        # To initialize variables
        totalSkuQtyAuExpressCannotBeMixed = 0
        totalSkuQtyAuExpressCanBeMixed = 0
        totalSkuPriceAuExpress = 0
        parcelId = 0

        parcelIdSet = set()
        parcelTableAuExpress = []

        # To initialize the table for processing (sorting columns)
        parcelAuExpress.sort_values(by=['can Be Mixed',
                                        'logistics Category Name Hash',
                                        'max Qty per Sku per Parcel StandAlone',
                                        'max Qty per Category per Parcel StandAlone'], 
                                    ascending=[True, True, False, False], 
                                    inplace=True)
        
        # For AuExpress
        # To retrieve parameters and calculate/populate parcel ID information
        for indexSku in range(parcelAuExpress.shape[0]):

            skuId = parcelAuExpress.iloc[indexSku]['sku Id']
            skuCount = parcelAuExpress.iloc[indexSku]['sku Count']
            skuWeight = parcelAuExpress.iloc[indexSku]['sku Weight']
            skuIdandAddOnServiceIds = parcelAuExpress.iloc[indexSku]['sku and Add-On Service ID List']
            
            sku = ProductSKU.objects.get(id=skuId)
            skuName = sku.name

            # To update the sku price back to AUD, 4.8 is the initial exchange rate used in Scrapy for database ingestion
            skuPrice = math.ceil(float(sku.price) / 4.8 * 10) / 10
            
            logisticsCategoryName = parcelAuExpress.iloc[indexSku]['logistics Category Name']
            logisticsCategoryNameHash = parcelAuExpress.iloc[indexSku]['logistics Category Name Hash']
            canBeMixed = parcelAuExpress.iloc[indexSku]['can Be Mixed']
            skuMaxQtyperSkuperParcelStandAlone = parcelAuExpress.iloc[indexSku]['max Qty per Sku per Parcel StandAlone']
            skuMaxQtyperCategoryperParcelStandAlone = parcelAuExpress.iloc[indexSku]['max Qty per Category per Parcel StandAlone']
            skuMaxQtyperParcelMixed = parcelAuExpress.iloc[indexSku]['max Qty per Parcel Mixed']
            skuExtraTax = parcelAuExpress.iloc[indexSku]['extra Tax']
            skuMaxTotalQtyperParcel = parcelAuExpress.iloc[indexSku]['max Total Qty per Parcel']
            skuMaxTotalWeightperParcel = parcelAuExpress.iloc[indexSku]['max Total Weight per Parcel']
            skuMaxTotalValueperParcel = parcelAuExpress.iloc[indexSku]['max Total Value per Parcel']
            skuLogisticsPrice = parcelAuExpress.iloc[indexSku]['logistics Price per Unit']
            skuLogisticsGst = parcelAuExpress.iloc[indexSku]['logistics Price Gst']

            # To loop through each one of a product
            for indexItem in range(skuCount):
                
                # For products that cannot be mixed in a parcel
                if canBeMixed == 0:
                    totalSkuQtyAuExpressCannotBeMixed += 1

                    # For the first item, initialize the parcel ID
                    if totalSkuQtyAuExpressCannotBeMixed == 1:
                        parcelId += 1

                    # Only do decision making for rows > 2
                    if totalSkuQtyAuExpressCannotBeMixed > 1:
                        parcelIdSet.add(parcelId)
                        parcelId = self.parcelIdIncrementCannotBeMixed(parcelTableAuExpress,
                                                                       parcelIdSet,
                                                                       parcelId,
                                                                       logisticsCategoryNameHash,
                                                                       canBeMixed,
                                                                       skuMaxQtyperCategoryperParcelStandAlone)
                            
                # For products that can be mixed in a parcel     
                elif canBeMixed == 1:
                    totalSkuQtyAuExpressCanBeMixed += 1

                    # For the first item, initialize the parcel ID
                    if totalSkuQtyAuExpressCanBeMixed == 1:
                        parcelId += 1

                    # Only do decision making for rows > 2
                    elif totalSkuQtyAuExpressCanBeMixed > 1:
                        parcelIdSet.add(parcelId)
                        parcelId = self.parcelIdIncrementCanBeMixed(parcelTableAuExpress,
                                                                    skuId,
                                                                    parcelIdSet,
                                                                    parcelId,
                                                                    logisticsCategoryNameHash,
                                                                    canBeMixed,
                                                                    skuMaxQtyperSkuperParcelStandAlone,
                                                                    skuMaxQtyperParcelMixed,
                                                                    skuMaxTotalQtyperParcel,
                                                                    skuMaxTotalWeightperParcel,
                                                                    skuMaxTotalValueperParcel)
                        
                parcelTableAuExpress.append([parcelId,
                                             skuId,
                                             1,
                                             skuWeight,
                                             skuIdandAddOnServiceIds,
                                             skuName,
                                             skuPrice,
                                             logisticsCategoryName,
                                             logisticsCategoryNameHash,
                                             canBeMixed,
                                             skuMaxQtyperSkuperParcelStandAlone,
                                             skuMaxQtyperCategoryperParcelStandAlone,
                                             skuMaxQtyperParcelMixed,
                                             skuExtraTax,
                                             skuMaxTotalQtyperParcel,
                                             skuMaxTotalWeightperParcel,
                                             skuMaxTotalValueperParcel,
                                             skuLogisticsPrice,
                                             skuLogisticsGst])

        parcelTableAuExpress = pd.DataFrame(parcelTableAuExpress, 
                                            columns=['parcel Id',
                                                     'sku Id',
                                                     'count In Parcel',
                                                     'sku Weight',
                                                     'sku and Add-On Service ID List',
                                                     'sku Name',
                                                     'sku Price',
                                                     'logistics Category Name',
                                                     'logistics Category Name Hash',
                                                     'can Be Mixed',
                                                     'max Qty per Sku per Parcel StandAlone',
                                                     'max Qty per Category per Parcel StandAlone',
                                                     'max Qty per Parcel Mixed',
                                                     'extra Tax',
                                                     'max Total Qty per Parcel',
                                                     'max Total Weight per Parcel',
                                                     'max Total Value per Parcel',
                                                     'logistics Price per Unit',
                                                     'logistics Price Gst'])
        
        # parcelTableAuExpress.to_csv('parcelTableAuExpress.csv', index=False)

        totalSkuPriceAuExpress = math.ceil(parcelTableAuExpress['sku Price'].astype(float).sum() * 10) / 10
        totalSkuPriceAuExpressCN = math.ceil(totalSkuPriceAuExpress * audExRate * 10) / 10

        # To prepare "parcelId_skuId_serviceId" list
        parcelTableAuExpress["parcelId skuId addOnServiceId"] = parcelTableAuExpress["parcel Id"].astype(str) + "_" + parcelTableAuExpress["sku and Add-On Service ID List"]
        parcelIdandSkuIdandAddOnServiceIdsListAuExpress = list(parcelTableAuExpress["parcelId skuId addOnServiceId"])

        ###########################################################################################
        # To construct the "parcelPackagingTableAuExpress" dictionary
        parcelIdAuExpressList = list(parcelTableAuExpress["parcel Id"].drop_duplicates(inplace=False))

        parcelPackagingTableAuExpress = dict()
        totalPostageAuExpress = 0
        for parcelIdAuExpressKey in parcelIdAuExpressList:
            temp = parcelTableAuExpress[parcelTableAuExpress['parcel Id'] == parcelIdAuExpressKey]

            tempSkuNameCountDf = pd.pivot_table(temp, index=['sku Name'], values=['count In Parcel'], aggfunc='sum').reset_index()

            countInParcelAndSkuNameList = []
            for index_count in range(tempSkuNameCountDf.shape[0]):

                tempSkuName = tempSkuNameCountDf.iloc[index_count]['sku Name']
                tempCountInParcel = tempSkuNameCountDf.iloc[index_count]['count In Parcel']

                countInParcelAndSkuNameList.append([tempCountInParcel, tempSkuName])

            # To get the total quantity and total weight of product in each parcelId
            productCountInParcelList = temp['count In Parcel'].sum()
            parcelWeight = math.ceil(temp['sku Weight'].astype(float).sum() * 10) / 10

            # parcel weight minimum count is 1Kg
            if parcelWeight < 1:
                parcelPostage = 1 * float(temp.iloc[0]['logistics Price per Unit'])
            else:
                parcelPostage = parcelWeight * float(temp.iloc[0]['logistics Price per Unit'])
            
            # To accumulate the postage in AUD
            parcelPostage = math.ceil(parcelPostage * 10) / 10
            parcelPostageCN = math.ceil(parcelPostage * audExRate * 10) / 10
            totalPostageAuExpress += parcelPostage

            # To contruct the element of dictionary
            parcelPackagingTableAuExpress[parcelIdAuExpressKey] = {'countInParcelAndSkuNameList': countInParcelAndSkuNameList,
                                                                   'productCountInParcelList': productCountInParcelList,
                                                                   'parcelWeight': parcelWeight,
                                                                   'parcelPostage': parcelPostage,
                                                                   'parcelPostageCN': parcelPostageCN}


        ###########################################################################################
        ###########################################################################################
        # To assign parcel ID for each product - EWE
        # To initialize variables
        totalSkuQtyEWECannotBeMixed = 0
        totalSkuQtyEWECanBeMixed = 0
        totalSkuPriceEWE = 0
        parcelId = 0

        parcelIdSet = set()
        parcelTableEWE = []

        # To initialize the table for processing (sorting columns)
        parcelEWE.sort_values(by=['can Be Mixed',
                                  'logistics Category Name Hash',
                                  'max Qty per Sku per Parcel StandAlone',
                                  'max Qty per Category per Parcel StandAlone'], 
                              ascending=[True, True, False, False], 
                              inplace=True)

        # For EWE
        # To retrieve parameters and calculate/populate parcel ID information
        for indexSku in range(parcelEWE.shape[0]):
            
            skuId = parcelEWE.iloc[indexSku]['sku Id']
            skuCount = parcelEWE.iloc[indexSku]['sku Count']
            skuWeight = parcelEWE.iloc[indexSku]['sku Weight']
            skuIdandAddOnServiceIds = parcelEWE.iloc[indexSku]['sku and Add-On Service ID List']
            
            sku = ProductSKU.objects.get(id=skuId)
            skuName = sku.name

            # To update the sku price back to AUD, 4.8 is the initial exchange rate used in Scrapy for database ingestion
            skuPrice = math.ceil(float(sku.price) / 4.8 * 10) / 10
            
            logisticsCategoryName = parcelEWE.iloc[indexSku]['logistics Category Name']
            logisticsCategoryNameHash = parcelEWE.iloc[indexSku]['logistics Category Name Hash']
            canBeMixed = parcelEWE.iloc[indexSku]['can Be Mixed']
            skuMaxQtyperSkuperParcelStandAlone = parcelEWE.iloc[indexSku]['max Qty per Sku per Parcel StandAlone']
            skuMaxQtyperCategoryperParcelStandAlone = parcelEWE.iloc[indexSku]['max Qty per Category per Parcel StandAlone']
            skuMaxQtyperParcelMixed = parcelEWE.iloc[indexSku]['max Qty per Parcel Mixed']
            skuExtraTax = parcelEWE.iloc[indexSku]['extra Tax']
            skuMaxTotalQtyperParcel = parcelEWE.iloc[indexSku]['max Total Qty per Parcel']
            skuMaxTotalWeightperParcel = parcelEWE.iloc[indexSku]['max Total Weight per Parcel']
            skuMaxTotalValueperParcel = parcelEWE.iloc[indexSku]['max Total Value per Parcel']
            skuLogisticsPrice = parcelEWE.iloc[indexSku]['logistics Price per Unit']
            skuLogisticsGst = parcelEWE.iloc[indexSku]['logistics Price Gst']

            # To loop through each quantity of a product
            for indexItem in range(skuCount):
                
                # For products that cannot be mixed in a parcel
                if canBeMixed == 0:
                    totalSkuQtyEWECannotBeMixed += 1

                    # For the first item, initialize the parcel ID
                    if totalSkuQtyEWECannotBeMixed == 1:
                        parcelId += 1

                    # Only do decision making for rows > 2
                    if totalSkuQtyEWECannotBeMixed > 1:
                        parcelIdSet.add(parcelId)
                        parcelId = self.parcelIdIncrementCannotBeMixed(parcelTableEWE,
                                                                       parcelIdSet,
                                                                       parcelId,
                                                                       logisticsCategoryNameHash,
                                                                       canBeMixed,
                                                                       skuMaxQtyperCategoryperParcelStandAlone)

                # For products that can be mixed in a parcel     
                elif canBeMixed == 1:
                    totalSkuQtyEWECanBeMixed += 1

                    # For the first item, initialize the parcel ID
                    if totalSkuQtyEWECanBeMixed == 1:
                        parcelId += 1

                    # Only do decision making for rows > 2
                    elif totalSkuQtyEWECanBeMixed > 1:
                        parcelIdSet.add(parcelId)
                        parcelId = self.parcelIdIncrementCanBeMixed(parcelTableEWE,
                                                                    skuId,
                                                                    parcelIdSet,
                                                                    parcelId,
                                                                    logisticsCategoryNameHash,
                                                                    canBeMixed,
                                                                    skuMaxQtyperSkuperParcelStandAlone,
                                                                    skuMaxQtyperParcelMixed,
                                                                    skuMaxTotalQtyperParcel,
                                                                    skuMaxTotalWeightperParcel,
                                                                    skuMaxTotalValueperParcel)
                        
                parcelTableEWE.append([parcelId,
                                       skuId,
                                       1,
                                       skuWeight,
                                       skuIdandAddOnServiceIds,
                                       skuName,
                                       skuPrice,
                                       logisticsCategoryName,
                                       logisticsCategoryNameHash,
                                       canBeMixed,
                                       skuMaxQtyperSkuperParcelStandAlone,
                                       skuMaxQtyperCategoryperParcelStandAlone,
                                       skuMaxQtyperParcelMixed,
                                       skuExtraTax,
                                       skuMaxTotalQtyperParcel,
                                       skuMaxTotalWeightperParcel,
                                       skuMaxTotalValueperParcel,
                                       skuLogisticsPrice,
                                       skuLogisticsGst])

        # To summarize the parcel ID packaging detail table
        parcelTableEWE = pd.DataFrame(parcelTableEWE, 
                                      columns=['parcel Id',
                                               'sku Id',
                                               'count In Parcel',
                                               'sku Weight',
                                               'sku and Add-On Service ID List',
                                               'sku Name',
                                               'sku Price',
                                               'logistics Category Name',
                                               'logistics Category Name Hash',
                                               'can Be Mixed',
                                               'max Qty per Sku per Parcel StandAlone',
                                               'max Qty per Category per Parcel StandAlone',
                                               'max Qty per Parcel Mixed',
                                               'extra Tax',
                                               'max Total Qty per Parcel',
                                               'max Total Weight per Parcel',
                                               'max Total Value per Parcel',
                                               'logistics Price per Unit',
                                               'logistics Price Gst'])
        
        # parcelTableEWE.to_csv('parcelTableEWE.csv', index=False)

        totalSkuPriceEWE = math.ceil(parcelTableEWE['sku Price'].astype(float).sum() * 10) / 10
        totalSkuPriceEWECN = math.ceil(totalSkuPriceEWE * audExRate * 10) / 10

        # To prepare "parcelId_skuId_serviceId123" list
        parcelTableEWE["parcelId skuId addOnServiceId"] = parcelTableEWE["parcel Id"].astype(str) + "_" + parcelTableEWE["sku and Add-On Service ID List"]
        parcelIdandSkuIdandAddOnServiceIdsListEWE = list(parcelTableEWE["parcelId skuId addOnServiceId"])

        ###########################################################################################
        # To construct the "parcelPackagingTableEWE" dictionary
        parcelIdEWEList = list(parcelTableEWE["parcel Id"].drop_duplicates(inplace=False))

        parcelPackagingTableEWE = dict()
        totalPostageEWE = 0
        for parcelIdEWEKey in parcelIdEWEList:
            temp = parcelTableEWE[parcelTableEWE['parcel Id'] == parcelIdEWEKey]

            tempSkuNameCountDf = pd.pivot_table(temp, index=['sku Name'], values=['count In Parcel'], aggfunc='sum').reset_index()

            countInParcelAndSkuNameList = []
            for index_count in range(tempSkuNameCountDf.shape[0]):

                tempSkuName = tempSkuNameCountDf.iloc[index_count]['sku Name']
                tempCountInParcel = tempSkuNameCountDf.iloc[index_count]['count In Parcel']

                countInParcelAndSkuNameList.append([tempCountInParcel, tempSkuName])

            # To get the total quantity and total weight of product in each parcelId
            productCountInParcelList = temp['count In Parcel'].sum()
            parcelWeight = math.ceil(temp['sku Weight'].astype(float).sum() * 10) / 10

            # parcel weight minimum count is 1Kg
            if parcelWeight < 1:
                parcelPostage = 1 * float(temp.iloc[0]['logistics Price per Unit'])
            else:
                parcelPostage = parcelWeight * float(temp.iloc[0]['logistics Price per Unit'])

            # To accumulate the postage in AUD
            parcelPostage = math.ceil(parcelPostage * 10) / 10
            parcelPostageCN = math.ceil(parcelPostage * audExRate * 10) / 10
            totalPostageEWE += parcelPostage

            # To contruct the element of dictionary
            parcelPackagingTableEWE[parcelIdEWEKey] = {'countInParcelAndSkuNameList': countInParcelAndSkuNameList,
                                                       'productCountInParcelList': productCountInParcelList,
                                                       'parcelWeight': parcelWeight, 
                                                       'parcelPostage': parcelPostage,
                                                       'parcelPostageCN': parcelPostageCN}


        ###########################################################################################
        ###########################################################################################
        # total pay = product price + postage price
        # AuExpress
        totalPostageAuExpress = math.ceil(totalPostageAuExpress * 10) / 10
        totalPostageAuExpressCN = math.ceil(totalPostageAuExpress * audExRate * 10) / 10

        totalPayAuExpress = math.ceil((float(totalSkuPriceAuExpress) + totalPostageAuExpress + float(totalServicePrice)) * 10) / 10
        totalPayAuExpressCN = math.ceil((totalSkuPriceAuExpressCN + totalPostageAuExpressCN + totalServicePriceCN) * 10) / 10
        
        # EWE
        totalPostageEWE = math.ceil(totalPostageEWE * 10) / 10
        totalPostageEWECN = math.ceil(totalPostageEWE * audExRate * 10) / 10

        totalPayEWE = math.ceil((float(totalSkuPriceEWE) + totalPostageEWE + float(totalServicePrice)) * 10) / 10
        totalPayEWECN = math.ceil((totalSkuPriceEWECN + totalPostageEWECN + totalServicePriceCN) * 10) / 10


        # To summarize the response
        context = {
            'audExRate': audExRate,
            'categories': categories,
            'senderAddresses': senderAddresses,
            'senderAddressDefault': senderAddressDefault,
            'receiverAddresses': receiverAddresses,
            'receiverAddressDefault': receiverAddressDefault,

            'skuIds': skuIds,
            'skuCountList': skuCountList,
            'skuIdandAddOnServiceIdsList': skuIdandAddOnServiceIdsList,
            'totalServiceQty': totalServiceQty,
            'totalServicePrice': totalServicePrice,
            'totalServicePriceCN': totalServicePriceCN,
            'totalLogisticsWeight': totalLogisticsWeight,
            
            'parcelPackagingTableAuExpress': parcelPackagingTableAuExpress,
            'parcelIdandSkuIdandAddOnServiceIdsListAuExpress': parcelIdandSkuIdandAddOnServiceIdsListAuExpress,
            'totalSkuQtyAuExpress': totalSkuQtyAuExpressCannotBeMixed + totalSkuQtyAuExpressCanBeMixed,
            'totalSkuPriceAuExpress': totalSkuPriceAuExpress,
            'totalSkuPriceAuExpressCN': totalSkuPriceAuExpressCN,
            'totalPostageAuExpress': totalPostageAuExpress,
            'totalPostageAuExpressCN': totalPostageAuExpressCN,
            'totalPayAuExpress': totalPayAuExpress,
            'totalPayAuExpressCN': totalPayAuExpressCN,
            
            'parcelPackagingTableEWE': parcelPackagingTableEWE,
            'parcelIdandSkuIdandAddOnServiceIdsListEWE': parcelIdandSkuIdandAddOnServiceIdsListEWE,
            'totalSkuQtyEWE': totalSkuQtyEWECannotBeMixed + totalSkuQtyEWECanBeMixed,
            'totalSkuPriceEWE': totalSkuPriceEWE,
            'totalSkuPriceEWECN': totalSkuPriceEWECN,
            'totalPostageEWE': totalPostageEWE,
            'totalPostageEWECN': totalPostageEWECN,
            'totalPayEWE': totalPayEWE,
            'totalPayEWECN': totalPayEWECN,
        }

        return render(request, 'orderPlace.html', context)


### To update the order related database tables, after review the order details, 
### like sender/receiver address, payment option, and parcel arrangements
class OrderCommitView(LoginRequiredMixin, View):
    
    @transaction.atomic
    def post(self, request):

        # To get the user
        user = request.user

        # To get the parameters
        skuIds = request.POST.get('skuIds')
        skuCountList = request.POST.get('skuCountList')

        senderAddressId = request.POST.get('senderAddressId')
        receiverAddressId = request.POST.get('receiverAddressId')

        logisticsCompanyName = request.POST.get('logisticsCompanyName')
        paymentMethod = int(request.POST.get('paymentMethod'))

        skuIdandAddOnServiceIdsList = request.POST.get('skuIdandAddOnServiceIdsList')
        parcelPackagingTable = request.POST.get('parcelPackagingTable')
        parcelIdandSkuIdandAddOnServiceIdsList = request.POST.get('parcelIdandSkuIdandAddOnServiceIdsList')

        totalSkuQty = request.POST.get('totalSkuQty')
        totalSkuPrice = request.POST.get('totalSkuPrice')
        
        totalServiceQty = request.POST.get('totalServiceQty')
        totalServicePrice = request.POST.get('totalServicePrice')
        
        totalLogisticsWeight = request.POST.get('totalLogisticsWeight')
        totalPostage = request.POST.get('totalPostage')

        totalPay = request.POST.get('totalPay')


        ###############################################################################################################
        ###############################################################################################################
        # To check if all parameters are provided, payment method is valid and addresses are provided
        if not all([skuIds, senderAddressId, receiverAddressId, paymentMethod, 
                    logisticsCompanyName, skuIdandAddOnServiceIdsList, parcelPackagingTable, parcelIdandSkuIdandAddOnServiceIdsList, 
                    totalSkuQty, totalSkuPrice, totalServiceQty, totalServicePrice, totalLogisticsWeight, totalPostage, totalPay]):
            return JsonResponse({'res': 1, 'errmsg': '参数不完整'})
        
        if paymentMethod not in OrderInfo.PAYMENT_METHODS.keys():
            return JsonResponse({'res': 2, 'errmsg': '非法支付方式'})

        try:
            sender = SenderAddress.objects.get(id=senderAddressId)
            senderAddr = sender.senderAddr
            senderTel = sender.senderTel
        except SenderAddress.DoesNotExist as e:
            return JsonResponse({'res': 3, 'errmsg': '寄件人地址待补充'})
        
        try:
            receiver = ReceiverAddress.objects.get(id=receiverAddressId)
            receiverAddr = receiver.receiverAddr
            receiverTel = receiver.receiverTel
        except ReceiverAddress.DoesNotExist as e:
            return JsonResponse({'res': 4, 'errmsg': '收件人地址待补充'})
        
        # To convert the "string" information to "list" information
        skuCountList = [ele.replace("'", "").replace(" ", "") for ele in skuCountList[1:-1].split(",")]
        skuIdandAddOnServiceIdsList = [ele.replace("'", "").replace(" ", "") for ele in skuIdandAddOnServiceIdsList[1:-1].split(",")]
        parcelPackagingTableList = [ele.replace("'", "").replace(" ", "") for ele in parcelPackagingTable[1:-2].split("}, ")]
        parcelIdandSkuIdandAddOnServiceIdsList = [ele.replace("'", "").replace(" ", "") for ele in parcelIdandSkuIdandAddOnServiceIdsList[1:-1].split(", ")]


        ###############################################################################################################
        ###############################################################################################################
        # To prepare data for "OrderInfo", "OrderProduct", "OrderProductandServiceMapping" and "OrderTracking" tables
        # Order Id: 20171122181630+用户id
        orderId = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)

        # orderNote: productName x quantity (service 1, service 2...)
        # skuIdCountTable
        indexItem = 0
        orderNotes = ""
        skuIdCountTable = []

        for skuIdandAddOnServiceIds in skuIdandAddOnServiceIdsList:
            
            # To get the corresponding sku count
            tempskuCount = skuCountList[indexItem]

            # To get the product name
            tempSkuId = skuIdandAddOnServiceIds.split("_")[0]
            tempSkuName = ProductSKU.objects.get(id=tempSkuId).name

            # To construct the skuIdCountTable, to prepare “skuId_quantity” list
            skuIdCountTable.append([tempSkuId, int(tempskuCount)])

            # To get the add-On service Id list
            tempAddOnServiceIds = skuIdandAddOnServiceIds.split("_")[1:]

            # If there is no add-On Service for the product
            if not tempAddOnServiceIds:

                # To concatenate message for orderNotes
                orderNotes = orderNotes + tempSkuName + " x " + str(tempskuCount) + "; "

            # If there is add-On Service for the product
            else:
                tempServiceNameStr = ""

                for tempAddOnServiceId in tempAddOnServiceIds:
                    tempAddOnServiceName = ProductAddOnService.objects.get(id=tempAddOnServiceId).name
                    tempServiceNameStr = tempServiceNameStr + tempAddOnServiceName + ", "

                # To remove the ", " for the last element
                tempServiceNameStr = tempServiceNameStr[:-2]

                # To concatenate message for orderNotes
                orderNotes = orderNotes + tempSkuName + " x " + str(tempskuCount) + " (" + tempServiceNameStr + "); "
            
            indexItem += 1

        # To calculate the "totalHandlingFee" based on payment type
        # 1. SuperPay - Wechat/Alipay: 1.0%, not included in the "totalprice"
        # 2. Strip - VISA/Master 3.5% + $0.3, included in the "totalprice"
        # 3. Bank Transfer
        totalPriceBeforeHandlingCost = float(totalSkuPrice) + float(totalServicePrice) + float(totalPostage)
        
        if paymentMethod == 1 or paymentMethod == 2:
            rateSuperPay = 0.01
            totalHandlingFee = totalPriceBeforeHandlingCost * rateSuperPay
            totalPrice = totalPriceBeforeHandlingCost
        
        elif paymentMethod == 3:
            rateStripe = 0.035
            totalHandlingFee = ((totalPriceBeforeHandlingCost + 0.3) / (1 - rateStripe)) * rateStripe + 0.3
            totalPrice = totalPriceBeforeHandlingCost + totalHandlingFee
        
        else:
            totalHandlingFee = 0
            totalPrice = totalPriceBeforeHandlingCost + totalHandlingFee

        # To construct “skuIdCount” list, via pivoting, one skuId/product per line, no duplicated skuIds in the table/list
        skuIdCountTable = pd.DataFrame(skuIdCountTable, columns=['sku Id', 'sku Count'])
        skuIdCountTable = pd.pivot_table(skuIdCountTable, index=['sku Id'], values=['sku Count'], aggfunc='sum').reset_index()
        skuIdCountTable["skuIdCount"] = skuIdCountTable["sku Id"].astype(str) + "_" + skuIdCountTable["sku Count"].astype(str)
        skuIdCountList = list(skuIdCountTable["skuIdCount"])

        # Configure the transaction save point
        saveId = transaction.savepoint()

        try:
            ###########################################################################################################
            # To add a record into "OrderInfo" table, 
            # orderStatus = 1 "UNPAID"
            # tradeNo pre-fill 0
            order = OrderInfo.objects.create(orderId=orderId,
                                             
                                             user=user,
                                             
                                             sender=sender,
                                             senderAddr=senderAddr,
                                             senderTel=senderTel,

                                             receiverAddressId=receiverAddressId,
                                             receiver=receiver,
                                             receiverAddr=receiverAddr,
                                             receiverTel=receiverTel,

                                             logisticsCompanyName=logisticsCompanyName,
                                             logisticsParcelCount=len(parcelPackagingTableList),

                                             paymentMethod=paymentMethod,
                                             
                                             totalSkuQty=totalSkuQty,
                                             totalSkuPrice=totalSkuPrice,

                                             totalServiceQty=totalServiceQty,
                                             totalServicePrice=totalServicePrice,
                                             
                                             totalLogisticsWeight=totalLogisticsWeight,
                                             logisticsUnit="Kg",
                                             totalLogisticsPrice=totalPostage,
                                             
                                             totalHandlingFee = totalHandlingFee,
                                             totalPrice=totalPrice,
                                             orderStatus=1,

                                             orderNotes=orderNotes,
                                             
                                             tradeNo="",
                                             paymentIntentDescription="",
                                             paymentInvoicePdfUrl="")


            ###########################################################################################################
            # To get and check the product information, to add a record into "OrderProduct" table
            for skuIdCount in skuIdCountList:
                
                # To try 3 times to update the "OrderProduct" Table
                for i in range(3):

                    # optimistic locking: no locking at query stage, but will cross check the "old stocking" when doing update, 
                    # if difference, it mean there is other people also updating the database
                    # pessimistic locking: locking at query stage

                    # If product exists
                    try:
                        skuId = skuIdCount.split("_")[0]
                        sku = ProductSKU.objects.get(id=skuId)
                    
                    # If product does not exist
                    except:
                        transaction.savepoint_rollback(saveId)
                        return JsonResponse({'res': 5, 'errmsg': '商品待补充'})


                    # To check if product has sufficient stock
                    skuCount = skuIdCount.split("_")[1]
                    if int(skuCount) > sku.stock:
                        transaction.savepoint_rollback(saveId)
                        return JsonResponse({'res': 6, 'errmsg': '商品库存不足'})

                    # To update the product stock and sales
                    orginStock = sku.stock
                    newStock = orginStock - int(skuCount)
                    newSales = sku.sales + int(skuCount)

                    # To update the product stock and sales, if the new checking stock same as the previous check stock,
                    # the update will be successful (=1), or fail (=0)
                    res = ProductSKU.objects.filter(id=skuId, stock=orginStock).update(stock=newStock, sales=newSales)

                    # If update fails
                    if res == 0:
                        
                        # If already 3 times
                        if i == 2:
                            
                            transaction.savepoint_rollback(saveId)
                            return JsonResponse({'res': 7, 'errmsg': '下单失败'})
                        
                        # If not 3 times yet, back to the for loop
                        else:
                            continue
                    
                    # To add a record into "OrderProduct" table
                    OrderProduct.objects.create(order=order,
                                                skuId=skuId,
                                                skuName=sku.name,
                                                skuCount=skuCount,
                                                skuUnit=sku.unit,
                                                skuPrice=math.ceil(float(sku.price) / 4.8 * 10) / 10,
                                                skuGst=math.ceil(float(sku.gst) / 4.8 * 10) / 10,
                                                comment="")
                    
                    # If update succeeds, break the for loop
                    break
            
            
            ###########################################################################################################
            # To get the add-on service information for each product in each parcel, to add a record into "OrderProductandServiceMapping" table
            skuIndex = 1
            for parcelIdandSkuIdandAddOnServiceIds in parcelIdandSkuIdandAddOnServiceIdsList:
                
                # To get the parcel Id, sku Id and add-on service Id list
                parcelId = int(parcelIdandSkuIdandAddOnServiceIds.split("_")[0])

                skuId = parcelIdandSkuIdandAddOnServiceIds.split("_")[1]
                skuName = ProductSKU.objects.get(id=skuId).name
                
                addOnServiceIds = parcelIdandSkuIdandAddOnServiceIds.split("_")[2:]
                
                # To get the add-on service Id if exist
                if addOnServiceIds:
                    for addOnServiceId in addOnServiceIds:

                        addOnService = ProductAddOnService.objects.get(id=addOnServiceId)
                        OrderProductandServiceMapping.objects.create(order=order,
                                                                     parcelId=parcelId,

                                                                     skuIndex=skuIndex,
                                                                     skuId=skuId,
                                                                     skuName=skuName,

                                                                     serviceName=addOnService.name,
                                                                     serviceImage="(待补充)",
                                                                     serviceUnit=addOnService.unit,
                                                                     servicePrice=addOnService.price,
                                                                     serviceGst=addOnService.gst)

                # To record "NA" or 0 if there is no add-on service associated with it
                else:
                    OrderProductandServiceMapping.objects.create(order=order,
                                                                 parcelId=parcelId,

                                                                 skuIndex=skuIndex,
                                                                 skuId=skuId,
                                                                 skuName=skuName,
                                                                 
                                                                 serviceName="无服务",
                                                                 serviceImage="无服务",
                                                                 serviceUnit="无服务",
                                                                 servicePrice=0,
                                                                 serviceGst=0)
            
                skuIndex += 1


            ###########################################################################################################
            # To get the parcel, product, service information, to add a record into "OrderTracking" table
            for parcelPackagingTable in parcelPackagingTableList:
                

                # 1:{countInParcelAndSkuNameList:[[3,AptaGrowNutrient-DenseMilkDrinkFrom1+Years900g]],productCountInParcelList:3,parcelWeight:3.0,parcelPostage:23.4,parcelPostageCN:111.3
                parcelPackagingTableItemList = parcelPackagingTable.split(":")
                parcelId = parcelPackagingTableItemList[0]
                skuQty = parcelPackagingTableItemList[3].split(",")[0]
                parcelWeight = parcelPackagingTableItemList[4].split(",")[0]
                parcelPostage = parcelPackagingTableItemList[5].split(",")[0]

                OrderTracking.objects.create(order=order,
                                             logisticsCompanyName=logisticsCompanyName,
                                             parcelId=parcelId,
                                             skuQty=skuQty,
                                             parcelWeight=parcelWeight,
                                             parcelPostage=parcelPostage,
                                             trackingId="(待补充)",
                                             trackingImage="(待补充)")

        except Exception as e:

            transaction.savepoint_rollback(saveId)
            return JsonResponse({'res': 7, 'errmsg': '下单失败'})

        # To commit the transaction
        transaction.savepoint_commit(saveId)

        # To clear shopping cart information from redis caching
        conn = get_redis_connection('default')
        cartKey = 'cart_%s' % user.id
        conn.delete(cartKey)

        # To return the "success" response
        return JsonResponse({'res': 8, 'message': '创建成功'})


### To show the order details, including service delivery and logistics image attachments
class OrderDetailsView(LoginRequiredMixin, View):
    
    ###################################################################################################################
    ###################################################################################################################
    def get(self, request, orderId):
        
        # To get the user information
        user = request.user

        ###########################################################################################
        ###########################################################################################
        # To check if orderId is genuine
        try:
            orderInfo = OrderInfo.objects.get(orderId=orderId)
        except OrderInfo.DoesNotExist as e:
            return redirect(reverse('user:order', kwargs={'page': 1}))

        try:
            orderProductandServiceMapping = OrderProductandServiceMapping.objects.filter(order=orderId)
        except OrderProductandServiceMapping.DoesNotExist as e:
            return redirect(reverse('user:order', kwargs={'page': 1}))
        
        try:
            orderTracking = OrderTracking.objects.filter(order=orderId)
        except OrderTracking.DoesNotExist as e:
            return redirect(reverse('user:order', kwargs={'page': 1}))


        ###########################################################################################
        ###########################################################################################
        # To get the order status text
        orderInfo.statusName = OrderInfo.ORDER_STATUS[orderInfo.orderStatus]
        orderInfo.methodName = OrderInfo.PAYMENT_METHODS[orderInfo.paymentMethod]
        orderInfo.receiverAddress = ReceiverAddress.objects.get(id=orderInfo.receiverAddressId)

        # To create a dictionary of parcel packaging information, including 
        # parcelId, logistics trackingID, logistics trackingImage, 
        # products inside the parcel, name and image
        # add-on service for each product, name and image, one product could have multiple add-on service
        parcelCount = orderInfo.logisticsParcelCount
        parcelPackagingandAddOnServiceDict = dict()
        skuList = []

        for parcelId in range(1, (parcelCount + 1)):

            orderTrackingParcel = orderTracking.filter(parcelId=parcelId)

            orderTrackingParcelTrackingId = orderTrackingParcel.values('trackingId')[0]['trackingId']
            orderTrackingParcelSkuQty = orderTrackingParcel.values('skuQty')[0]['skuQty']
            orderTrackingParcelParcelWeight = orderTrackingParcel.values('parcelWeight')[0]['parcelWeight']
            orderTrackingParcelTrackingImage = orderTrackingParcel.values('trackingImage')[0]['trackingImage']


            # To get the product list within a parcel
            orderProductandServiceMapping = OrderProductandServiceMapping.objects.filter(order=orderId).filter(parcelId=parcelId)
            skuIndexList = orderProductandServiceMapping.values_list('skuIndex', flat=True).distinct()

            for skuIndex in skuIndexList:

                # To get the add-on Service
                orderProductandServiceMappingSkuItem = orderProductandServiceMapping.filter(skuIndex=skuIndex)

                skuId = orderProductandServiceMappingSkuItem.values('skuId')[0]['skuId']
                sku = ProductSKU.objects.get(id=skuId)
                sku.orderProductandServiceMappingSkuItem = orderProductandServiceMappingSkuItem


                skuList.append(sku)
            
            parcelPackagingandAddOnServiceDict[parcelId] = {
                'orderTrackingParcelTrackingId': orderTrackingParcelTrackingId,
                'orderTrackingParcelSkuQty': orderTrackingParcelSkuQty,
                'orderTrackingParcelParcelWeight': orderTrackingParcelParcelWeight,
                'orderTrackingParcelTrackingImage': orderTrackingParcelTrackingImage,
                'skuList': skuList,
            }
            skuList = []


        ###########################################################################################
        ###########################################################################################
        # To prepare output parameters
        context = {
            'audExRate': audExRate,
            'orderId': str(orderId),
            'orderInfo': orderInfo,
            'parcelPackagingandAddOnServiceDict': parcelPackagingandAddOnServiceDict,
        }

        return render(request, 'orderDetails.html', context)


### To create payment checkout view
class CreateCheckoutSessionView(LoginRequiredMixin, View):
    
    def post(self, request, *args, **kwargs):
        
        # To get the user information
        user = request.user

        # To get the parameter passed through
        orderId = self.kwargs["orderId"]
        orderInfo = OrderInfo.objects.get(orderId=orderId)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        

        checkoutSession = stripe.checkout.Session.create(
            client_reference_id=orderId,
            customer_email=user.email,
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'AUD',
                        'unit_amount': int(math.ceil(float(orderInfo.totalSkuPrice) * 10) / 10 * 100),
                        'product_data': {
                            'name': "Total Product Price",
                        },
                    },
                    'quantity': 1,
                },
                {
                    'price_data': {
                        'currency': 'AUD',
                        'unit_amount': int(math.ceil(float(orderInfo.totalServicePrice) * 10) / 10 * 100),
                        'product_data': {
                            'name': "Total Add-On Service Price",
                        },
                    },
                    'quantity': 1,
                },
                {
                    'price_data': {
                        'currency': 'AUD',
                        'unit_amount': int(math.ceil(float(orderInfo.totalLogisticsPrice) * 10) / 10 * 100),
                        'product_data': {
                            'name': "Total Logistics Price",
                        },
                    },
                    'quantity': 1,
                },
                {
                    'price_data': {
                        'currency': 'AUD',
                        'unit_amount': int(math.ceil(float(orderInfo.totalHandlingFee) * 10) / 10 * 100),
                        'product_data': {
                            'name': "Total Transaction Handling Fee",
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "orderId": orderInfo.orderId
            },
            mode='payment',
            customer_creation='always',
            success_url=os.getenv("STRIPE_REDIRECT_DOMAIN") + '/order/checkoutsuccess',
            cancel_url=os.getenv("STRIPE_REDIRECT_DOMAIN") + '/order/checkoutcancel',

            invoice_creation={
                "enabled": True,
                "invoice_data": {
                    "description": orderInfo.orderNotes,
                }
            }
        )


        return JsonResponse({'id': checkoutSession.id})


### To create checkout success view
class CheckoutSuccessView(LoginRequiredMixin, View):
    
    def get(self, request):

        return render(request, 'checkoutSuccess.html', {'audExRate': audExRate})


### To create checkout cancel view
class CheckoutCancelView(LoginRequiredMixin, View):
    
    def get(self, request):

        return render(request, 'checkoutCancel.html', {'audExRate': audExRate})


### To create web hook for "Stripe"
@csrf_exempt
def stripeWebhook(request):

    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':

        print("checkout.session.completed", event)

        session = event['data']['object']

        print("checkout.session.completed", session)

        customerEmail = session["customer_details"]["email"]
        orderId = session["metadata"]["orderId"]
        paymentIntentDescription = session["payment_intent"]

        # To update the "OrderInfo"
        OrderInfo.objects.filter(orderId=orderId).update(
            orderStatus=2,
            paymentIntentDescription=paymentIntentDescription,
            )

        # Send payment successful email via celery delay queue
        sendPaymentSuccessEmail.delay(customerEmail, orderId)

    if event['type'] == 'invoice.sent':

        print("invoice.sent", event)

        session = event['data']['object']

        print("invoice.sent", session)

        paymentIntentDescription = session["payment_intent"]
        charge = session["charge"]
        invoicePdfUrl = session["invoice_pdf"]

        print(paymentIntentDescription)
        print(charge)
        print(invoicePdfUrl)

        orderId = OrderInfo.objects.get(paymentIntentDescription=paymentIntentDescription).orderId
        s3Url = uploadPdfToS3(invoicePdfUrl, f'media/paymentInvoicePdf/{orderId}-Invoice.pdf')
        OrderInfo.objects.filter(paymentIntentDescription=paymentIntentDescription).update(
            tradeNo=charge,
            paymentInvoicePdfUrl=f'paymentInvoicePdf/{orderId}-Invoice.pdf'
            )

    return HttpResponse(status=200)


### To create web hook for "Supay WeChat Pay"
@csrf_exempt
def weChatPayWebhook(request):

    noticeId = request.GET.get('notice_id')
    merchantTradeNo = request.GET.get('merchant_trade_no')
    token = request.GET.get('token')

    paramsNotificationURL = {
		'notice_id': noticeId,
        'merchant_trade_no': merchantTradeNo,
        'authentication_code': settings.AUTHENTICATION_CODE,
	}

    encodedParamsNotificationURL = urlencode(paramsNotificationURL, quote_via=quote)
    md5HashedParamsNotificationURL = hashlib.md5(encodedParamsNotificationURL.encode()).hexdigest()

    # To check if the token provided is same as the local generation
    if token == md5HashedParamsNotificationURL:

        url = 'https://api.superpayglobal.com/payment/bridge/notification_verification'
        
        paramsNotificationValidation = {
            'notice_id': noticeId,
            'merchant_trade_no': merchantTradeNo,
        }

        response = requests.get(url, params=paramsNotificationValidation)

        if response.status_code == 200:
            # Parse the JSON response
            responseData = response.json()
            
            # Check if the response indicates success
            if responseData['result'] == 'SUCCESS':
                print('Notification validation successful')

                orderInfo = OrderInfo.objects.get(orderId=merchantTradeNo)
                user = orderInfo.user
                customerEmail = user.email

                # To update the "OrderInfo"
                OrderInfo.objects.filter(orderId=merchantTradeNo).update(
                    orderStatus=2,
                    paymentIntentDescription="WeChatPay",
                    )

                # Send payment successful email via celery delay queue
                sendPaymentSuccessEmail.delay(customerEmail, merchantTradeNo)

            else:
                sendWeChatPaynentFailureEmail.delay('info@auking.com.au', merchantTradeNo, "Notification validation failed")
        
        else:
            print('Error:', response.status_code)
            sendWeChatPaynentFailureEmail.delay('info@auking.com.au', merchantTradeNo, response.status_code)
        

    return HttpResponse(status=200)


### To create web hook for "Supay Ali Pay"
@csrf_exempt
def aliPayWebhook(request):

    noticeId = request.GET.get('notice_id')
    merchantTradeNo = request.GET.get('merchant_trade_no')
    token = request.GET.get('token')

    paramsNotificationURL = {
		'notice_id': noticeId,
        'merchant_trade_no': merchantTradeNo,
        'authentication_code': settings.AUTHENTICATION_CODE,
	}

    encodedParamsNotificationURL = urlencode(paramsNotificationURL, quote_via=quote)
    md5HashedParamsNotificationURL = hashlib.md5(encodedParamsNotificationURL.encode()).hexdigest()

    # To check if the token provided is same as the local generation
    if token == md5HashedParamsNotificationURL:

        url = 'https://api.superpayglobal.com/payment/bridge/notification_verification'
        
        paramsNotificationValidation = {
            'notice_id': noticeId,
            'merchant_trade_no': merchantTradeNo,
        }

        response = requests.get(url, params=paramsNotificationValidation)

        if response.status_code == 200:
            # Parse the JSON response
            responseData = response.json()
            
            # Check if the response indicates success
            if responseData['result'] == 'SUCCESS':
                print('Notification validation successful')

                orderInfo = OrderInfo.objects.get(orderId=merchantTradeNo)
                user = orderInfo.user
                customerEmail = user.email

                # To update the "OrderInfo"
                OrderInfo.objects.filter(orderId=merchantTradeNo).update(
                    orderStatus=2,
                    paymentIntentDescription="AliPay",
                    )

                # Send payment successful email via celery delay queue
                sendPaymentSuccessEmail.delay(customerEmail, merchantTradeNo)

            else:
                sendWeChatPaynentFailureEmail.delay('info@auking.com.au', merchantTradeNo, "Notification validation failed")
        
        else:
            print('Error:', response.status_code)
            sendWeChatPaynentFailureEmail.delay('info@auking.com.au', merchantTradeNo, response.status_code)
        

    return HttpResponse(status=200)


### To upload the invoice PDF from Stripe to AWS S3 /media/paymentInvoicePdf
def uploadPdfToS3(pdfUrl, s3Path):

    # Download the PDF file from the URL
    response = requests.get(pdfUrl)

    if response.status_code == 200:

        # Create a BytesIO object to hold the PDF content
        pdfBytes = BytesIO(response.content)

        # Connect to your S3 bucket
        s3 = boto3.client("s3", aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"))

        # Upload the PDF file to your S3 bucket
        s3Bucket = os.getenv("AWS_STORAGE_BUCKET_NAME")
        s3.upload_fileobj(pdfBytes, s3Bucket, s3Path)

        # Return the S3 URL of the uploaded file
        s3Url = f"https://{s3Bucket}.s3.ap-southeast-2.amazonaws.com/{s3Path}"

        return s3Url
    else:

        print("Failed to download PDF file from URL:", response.status_code)
        return None


### To display the link expiration message and setup redirection to "register" page
class BankTransferDetailsView(View):

    def get(self, request):

        return render(request, 'bankTransferDetails.html', {'audExRate': audExRate})

