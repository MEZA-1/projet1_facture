from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'address','sex','city','zipe_code','created_date','save_by')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('customer', 'invoice_type', 'total_amount', 'paid', 'last_update_date_time', 'save_by')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'product', 'quantity', 'unit_price')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_price', 'description', 'created_date', 'save_by') 

admin.site.site_header = "Invoice Management System Admin"
admin.site.site_title = "Invoice Management System Admin Portal"
admin.site.index_title = "Welcome to the Invoice Management System Admin Portal"