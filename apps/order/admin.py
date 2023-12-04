from django.contrib import admin
from django.http import HttpResponse
import csv

# Register your models here.
from .models import OrderInfo, OrderProduct, OrderProductandServiceMapping, OrderTracking


class OrderInfoAdmin(admin.ModelAdmin):
    list_display = ("orderId", "user", "sender", "senderAddr", "senderTel", "receiverAddressId", "receiver", "receiverAddr", "receiverTel",\
                    "logisticsCompanyName", "logisticsParcelCount", "paymentMethod",\
                    "totalSkuQty", "totalSkuPrice", "totalServiceQty", "totalServicePrice",\
                    "totalLogisticsWeight", "logisticsUnit", "totalLogisticsPrice",\
                    "totalHandlingFee", "totalPrice", "orderStatus", "orderNotes", "tradeNo")
    list_filter = ("sender", "receiver", "logisticsCompanyName", "paymentMethod", "orderStatus")
    search_fields = ("orderId", "user__user", "sender", "senderAddr", "senderTel", "receiver", "receiverAddr", "receiverTel",\
                     "logisticsCompanyName", "paymentMethod", "orderNotes", "tradeNo")

    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = OrderInfo._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class OrderProductAdmin(admin.ModelAdmin):
    list_display = ("order", "skuId", "skuName", "skuCount", "skuUnit", "skuPrice", "skuGst", "comment")
    list_filter = ("order__orderId", "skuName")
    search_fields = ("order__orderId", "skuName", "comment")

    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = OrderProduct._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class OrderProductandServiceMappingAdmin(admin.ModelAdmin):
    list_display = ("order", "parcelId", "skuIndex", "skuId", "skuName", "serviceName", "serviceImage", "serviceUnit", "servicePrice", "serviceGst")
    list_filter = ("order__orderId", "parcelId", "skuName", "serviceName")
    search_fields = ("order__orderId", "parcelId", "skuName", "serviceName")

    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = OrderProductandServiceMapping._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ("order", "logisticsCompanyName", "parcelId", "skuQty", "parcelWeight", "parcelPostage", "trackingId", "trackingImage")
    list_filter = ("order__orderId", "logisticsCompanyName", "parcelId", "trackingId")
    search_fields = ("order__orderId", "logisticsCompanyName", "parcelId", "trackingId")

    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = OrderTracking._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


admin.site.register(OrderInfo, OrderInfoAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
admin.site.register(OrderProductandServiceMapping, OrderProductandServiceMappingAdmin)
admin.site.register(OrderTracking, OrderTrackingAdmin)
