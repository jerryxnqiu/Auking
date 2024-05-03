from typing import Any, Dict, Mapping, Optional, Type, Union
from django.contrib import admin, messages
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import path, reverse
from django import forms
from tinymce.widgets import TinyMCE
from django.db import models
import csv

# Register your models here.
from .models import ProductLogisticsAuExpress, ProductLogisticsEWE, ProductAddOnService, ProductFromScrapy,\
                    ProductCategory, ProductSubCategory, ProductSPU, ProductSKU, ProductImage,\
                    IndexProductBanner, IndexPromotionBanner, IndexCategoryProductBanner, BulkPurchaseDiscount


class CsvImportForm(forms.Form):
    csv_upload = forms.FileField()


class ProductLogisticsAuExpressAdmin(admin.ModelAdmin):
    list_display = ("name", "canBeMixed", "maxQtyperSkuperParcelStandAlone", "maxQtyperCategoryperParcelStandAlone", \
                    "maxQtyperParcelMixed", "extraTax", "maxTotalQtyperParcel", "maxTotalWeightperParcel", "maxTotalValueperParcel", \
                    "price", "gst", "unit")
    list_filter = ("canBeMixed", "maxQtyperSkuperParcelStandAlone", "maxQtyperCategoryperParcelStandAlone", \
                   "maxQtyperParcelMixed", "maxTotalQtyperParcel", "maxTotalWeightperParcel", "maxTotalValueperParcel")
    search_fields = ["name"]

    def get_urls(self):

        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]

        return new_urls + urls


    def upload_csv(self, request):
        
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]

            for x in csv_data:
                fields = x.split(",")
                created = ProductLogisticsAuExpress.objects.update_or_create(
                    name = fields[0],
                    canBeMixed = fields[1],
                    maxQtyperSkuperParcelStandAlone = fields[2],
                    maxQtyperCategoryperParcelStandAlone = fields[3],
                    maxQtyperParcelMixed = fields[4],
                    extraTax = fields[5],
                    maxTotalQtyperParcel = fields[6],
                    maxTotalWeightperParcel = fields[7],
                    maxTotalValueperParcel = fields[8],
                    price = fields[9],
                    gst = fields[10],
                    unit = fields[11],
                    )
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
     
        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = ProductLogisticsAuExpress._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class ProductLogisticsEWEAdmin(admin.ModelAdmin):
    list_display = ("name", "canBeMixed", "maxQtyperSkuperParcelStandAlone", "maxQtyperCategoryperParcelStandAlone", \
                    "maxQtyperParcelMixed", "extraTax", "maxTotalQtyperParcel", "maxTotalWeightperParcel", "maxTotalValueperParcel", \
                    "price", "gst", "unit")
    list_filter = ("canBeMixed", "maxQtyperSkuperParcelStandAlone", "maxQtyperCategoryperParcelStandAlone", \
                   "maxQtyperParcelMixed", "maxTotalQtyperParcel", "maxTotalWeightperParcel", "maxTotalValueperParcel")
    search_fields = ["name"]


    def get_urls(self):

        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]

        return new_urls + urls


    def upload_csv(self, request):
        
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]

            for x in csv_data:
                fields = x.split(",")
                created = ProductLogisticsEWE.objects.update_or_create(
                    name = fields[0],
                    canBeMixed = fields[1],
                    maxQtyperSkuperParcelStandAlone = fields[2],
                    maxQtyperCategoryperParcelStandAlone = fields[3],
                    maxQtyperParcelMixed = fields[4],
                    extraTax = fields[5],
                    maxTotalQtyperParcel = fields[6],
                    maxTotalWeightperParcel = fields[7],
                    maxTotalValueperParcel = fields[8],
                    price = fields[9],
                    gst = fields[10],
                    unit = fields[11],
                    )
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
     
        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = ProductLogisticsEWE._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class ProductAddOnServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "gst", "unit")
    search_fields = ["name"]

    def get_urls(self):

        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]

        return new_urls + urls


    def upload_csv(self, request):
        
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]

            for x in csv_data:
                fields = x.split(",")
                created = ProductAddOnService.objects.update_or_create(
                    name = fields[0],
                    price = fields[1],
                    gst = fields[2],
                    unit = fields[3],
                    )
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
     
        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)
    

    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = ProductAddOnService._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class ProductFromScrapyAdmin(admin.ModelAdmin):
    list_display = ("category", "subCategory", "spu", "lv1BreadcrumbsName", "lv2BreadcrumbsName", "lv3BreadcrumbsName", "lv4BreadcrumbsName", "lv5BreadcrumbsName",\
                    "sourceName", "sourceNameAndId", "name", "brand", "description", "cost", "price", "gst", \
                    "unit", "imageThumbNail", "imageProductPage", "weight", "logisticsCategoryAuExpress", "logisticsCategoryEWE")
    list_filter = ("category", "subCategory", "spu", "lv1BreadcrumbsName", "lv2BreadcrumbsName", "lv3BreadcrumbsName", "lv4BreadcrumbsName", "lv5BreadcrumbsName",\
                   "brand", "weight", "logisticsCategoryAuExpress", "logisticsCategoryEWE")
    search_fields = ("sourceName", "sourceNameAndId", "name", "brand", "description")

    def get_urls(self):

        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]

        return new_urls + urls


    def upload_csv(self, request):
        
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]
            
            for x in csv_data:
                fields = x.split(",")

                created = ProductSKU.objects.update_or_create(
                        category = fields[0],
                        subCategory = fields[1],
                        spu = fields[2],

                        lv1BreadcrumbsName = fields[3],
                        lv2BreadcrumbsName = fields[4],
                        lv3BreadcrumbsName = fields[5],
                        lv4BreadcrumbsName = fields[6],
                        lv5BreadcrumbsName = fields[7],

                        sourceName = fields[8],
                        sourceNameAndId = fields[9],
                        
                        name = fields[10],
                        brand = fields[11],
                        description = fields[12],
                        cost = fields[13],
                        price = fields[14],
                        gst = fields[15],
                        unit = fields[16],

                        imageThumbNail = fields[17],
                        imageProductPage = fields[18],
                        weight = fields[19],

                        logisticsCategoryAuExpress = ProductLogisticsAuExpress.objects.get(name=fields[20]),
                        logisticsCategoryEWE = ProductLogisticsEWE.objects.get(name=fields[20]),

                        )
                

            url = reverse('admin:index')
            return HttpResponseRedirect(url)
     
        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = ProductSKU._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "nameCN", "logo", "image", "detail")
    search_fields = ("name", "nameCN")

    def get_urls(self):

        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]

        return new_urls + urls


    def upload_csv(self, request):
        
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]

            for x in csv_data:
                fields = x.split(",")
                created = ProductCategory.objects.update_or_create(
                    name = fields[0],
                    nameCN = fields[1],
                    logo = fields[2],
                    image = fields[3],
                    detail = fields[4],
                    )
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
     
        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = ProductCategory._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response

    export_as_csv.short_description = 'Export as CSV'


class ProductSubCategoryAdmin(admin.ModelAdmin):
    list_display = ("category", "name", "nameCN", "detail")
    list_filter = ("category__name", "name", "nameCN")
    search_fields = ("category__name", "name", "nameCN", "detail")

    def get_urls(self):

        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]

        return new_urls + urls


    def upload_csv(self, request):
        
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]

            for x in csv_data:
                fields = x.split(",")
                created = ProductSubCategory.objects.update_or_create(
                    category = ProductCategory.objects.get(name=fields[0]),
                    name = fields[1],
                    nameCN = fields[2],
                    detail = fields[3],
                    )
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
     
        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = ProductSubCategory._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class ProductSPUAdmin(admin.ModelAdmin):
    list_display = ("category", "subCategory", "name", "nameCN", "detail")
    list_filter = ("category__name", "subCategory__name", "name", "nameCN")
    search_fields = ("category__name", "subCategory__name", "name", "nameCN", "detail")

    def get_urls(self):

        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]

        return new_urls + urls


    def upload_csv(self, request):
        
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]

            for x in csv_data:
                fields = x.split(",")
                created = ProductSPU.objects.update_or_create(
                    category = ProductCategory.objects.get(name=fields[0]),
                    subCategory = ProductSubCategory.objects.get(name=fields[1]),
                    name = fields[2],
                    nameCN = fields[3],
                    detail = fields[4],
                    )
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
    
        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = ProductSPU._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class ProductSKUAdmin(admin.ModelAdmin):
    list_display = ("category", "subCategory", "spu", "sourceNameAndId", "name", "nameCN", "brand", "description", "cost", "price", "gst", \
                    "unit", "image", "weight", "stock", "sales", "logisticsCategoryAuExpress", "logisticsCategoryEWE", "onsales", "status")
    list_filter = ("category__name", "subCategory__name", "spu__name", "brand", "cost", "price", \
                   "unit", "weight", "stock", "logisticsCategoryAuExpress", "logisticsCategoryEWE", "onsales", "sales")
    search_fields = ("sourceNameAndId", "name", "nameCN", "brand", "description")

    def get_urls(self):

        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]

        return new_urls + urls


    def upload_csv(self, request):
        
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]
            
            for x in csv_data:
                fields = x.split(",")

                created = ProductSKU.objects.update_or_create(
                        category = ProductCategory.objects.get(name=fields[0]),
                        subCategory = ProductSubCategory.objects.get(name=fields[1]),
                        spu = ProductSPU.objects.get(name=fields[2]),

                        sourceNameAndId = fields[3],
                        name = fields[4],
                        nameCN = fields[5],

                        brand = fields[6],
                        description = fields[7],
                        cost = fields[8],
                        price = fields[9],
                        gst = fields[10],
                        unit = fields[11],

                        image = fields[12],

                        weight = fields[13],
                        stock = fields[14],
                        sales = fields[15],

                        logisticsCategoryAuExpress = ProductLogisticsAuExpress.objects.get(name=fields[16]),
                        logisticsCategoryEWE = ProductLogisticsEWE.objects.get(name=fields[17]),
                        
                        onsales = fields[18],
                        status = fields[19],
                        )
                

            url = reverse('admin:index')
            return HttpResponseRedirect(url)
     
        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = ProductSKU._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("sku", "image")
    search_fields = ["sku__name"]

    def get_urls(self):

        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]

        return new_urls + urls


    def upload_csv(self, request):
        
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]

            for x in csv_data:
                fields = x.split(",")
                # print(len(fields[1]))
                created = ProductImage.objects.update_or_create(
                    sku = ProductSKU.objects.get(name=fields[0]),
                    image = fields[1].replace("\r", ""),
                    )
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
     
        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = ProductImage._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class IndexProductBannerAdmin(admin.ModelAdmin):
    list_display = ("name", "image", "index")
    search_fields = ["name"]

    def get_urls(self):

        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]

        return new_urls + urls


    def upload_csv(self, request):
        
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]

            for x in csv_data:
                fields = x.split(",")
                created = IndexProductBanner.objects.update_or_create(
                    name = fields[0],
                    image = fields[1],
                    index = fields[2],
                    )
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
     
        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = IndexProductBanner._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class IndexPromotionBannerAdmin(admin.ModelAdmin):
    list_display = ("name", "url", "image", "discount", "index")
    list_filter = ["discount"]
    search_fields = ["name"]

    def get_urls(self):

        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]

        return new_urls + urls


    def upload_csv(self, request):
        
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]

            for x in csv_data:
                fields = x.split(",")
                created = IndexPromotionBanner.objects.update_or_create(
                    name = fields[0],
                    url = fields[1],
                    image = fields[2],
                    discount = fields[3],
                    index = fields[4],
                    )
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
     
        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = IndexPromotionBanner._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class IndexCategoryProductBannerAdmin(admin.ModelAdmin):
    list_display = ("category", "subCategory", "spu", "sku", "displayCategory", "index")
    list_filter = ("category__name", "subCategory__name", "spu__name", "displayCategory")
    search_fields = ("category__name", "subCategory__name", "spu__name", "sku__name", "displayCategory")

    def get_urls(self):

        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]

        return new_urls + urls


    def upload_csv(self, request):
        
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]

            for x in csv_data:
                fields = x.split(",")
                created = IndexCategoryProductBanner.objects.update_or_create(
                    category = ProductCategory.objects.get(name=fields[0]),
                    subCategory = ProductSubCategory.objects.get(name=fields[1]),
                    spu = ProductSPU.objects.get(name=fields[2]),
                    sku = ProductSKU.objects.get(name=fields[3]),
                    displayCategory = fields[4],
                    index = fields[5],
                    )
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
     
        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = IndexCategoryProductBanner._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class BulkPurchaseDiscountAdmin(admin.ModelAdmin):
    list_display = ("category", "subCategory", "stopQuantity", "progressiveDiscount")
    list_filter = ("category__name", "subCategory__name")
    search_fields = ("category__name", "subCategory__name")

    def get_urls(self):

        urls = super().get_urls()
        new_urls = [path('upload-csv/', self.upload_csv),]

        return new_urls + urls


    def upload_csv(self, request):
        
        if request.method == "POST":
            csv_file = request.FILES["csv_upload"]
            
            if not csv_file.name.endswith('.csv'):
                messages.warning(request, 'The wrong file type was uploaded')
                return HttpResponseRedirect(request.path_info)
            
            file_data = csv_file.read().decode("utf-8")
            csv_data = file_data.split("\n")[1:]

            for x in csv_data:
                fields = x.split(",")
                created = BulkPurchaseDiscount.objects.update_or_create(
                    category = ProductCategory.objects.get(name=fields[0]),
                    subCategory = ProductSubCategory.objects.get(name=fields[1]),
                    stopQuantity = fields[2],
                    progressiveDiscount = fields[3],
                    )
            url = reverse('admin:index')
            return HttpResponseRedirect(url)
     
        form = CsvImportForm()
        data = {"form": form}

        return render(request, "admin/csv_upload.html", data)


    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = BulkPurchaseDiscount._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'



admin.site.register(ProductLogisticsAuExpress, ProductLogisticsAuExpressAdmin)
admin.site.register(ProductLogisticsEWE, ProductLogisticsEWEAdmin)
admin.site.register(ProductAddOnService, ProductAddOnServiceAdmin)
admin.site.register(ProductFromScrapy, ProductFromScrapyAdmin)

admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ProductSubCategory, ProductSubCategoryAdmin)
admin.site.register(ProductSPU, ProductSPUAdmin)
admin.site.register(ProductSKU, ProductSKUAdmin)
admin.site.register(ProductImage, ProductImageAdmin)

admin.site.register(IndexProductBanner, IndexProductBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
admin.site.register(IndexCategoryProductBanner, IndexCategoryProductBannerAdmin)
admin.site.register(BulkPurchaseDiscount, BulkPurchaseDiscountAdmin)
