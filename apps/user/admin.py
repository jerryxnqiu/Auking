from django.contrib import admin
from django.http import HttpResponse
from django import forms
import csv

# Register your models here.
from .models import User, SenderAddress, ReceiverAddress

class UserAdmin(admin.ModelAdmin):
    list_display = ("last_login", "is_superuser", "username", "email",\
                    "is_staff", "is_staff", "is_active", "date_joined",\
                    "is_delete")

    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = User._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'

class SenderAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "sender", "senderAddr", "senderTel", "isDefault")

    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = SenderAddress._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


class ReceiverAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "receiver", "receiverAddr", "receiverIdImageFront", "receiverIdImageBack", "receiverTel", "isDefault")

    actions = ['export_as_csv']
    def export_as_csv(self, request, queryset):
        meta = ReceiverAddress._meta
        fieldNames = [field.name for field in meta.fields]
        response = HttpResponse(content_type = 'text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)
        writer.writerow(fieldNames)

        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fieldNames])

        return response
    
    export_as_csv.short_description = 'Export as CSV'


admin.site.register(User, UserAdmin)
admin.site.register(SenderAddress, SenderAddressAdmin)
admin.site.register(ReceiverAddress, ReceiverAddressAdmin)
