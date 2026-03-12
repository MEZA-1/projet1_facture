from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'address','sex','city','zipe_code','created_date','save_by')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'invoice_type', 'total_amount', 'paid', 'last_update_date_time', 'invoice_date_time', 'save_by','is_annuler')
    readonly_fields = ('total_amount',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_price', 'description', 'created_date', 'save_by', 'quantity_in_stock', 'quantity_seiled',) 

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product', 'quantity','total_price', 'unit_price')
    readonly_fields = ('total_price', 'unit_price')


admin.site.site_header = "Invoice Management System Admin"
admin.site.site_title = "Invoice Management System Admin Portal"
admin.site.index_title = "Welcome to the Invoice Management System Admin Portal"
