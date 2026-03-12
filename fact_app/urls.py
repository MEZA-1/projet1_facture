from django.urls import path
from . import views
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('add-customer', views.AddCustomerView.as_view(), name='add-customer'),
    path('add-invoice/', views.AddInvoiceView.as_view(), name='add-invoice'),
    #path('products/<int:product_id>/info/', views.product_info, name='product-info'),
    path('view-invoice/<int:pk>',views.InvoiceVisualizationView.as_view(), name='view-invoice'),
    path('get-imvoice-pdf/<int:pk>',views.get_imvoice_pdf, name="get-imvoice-pdf"),
    path('add-product', views.AddproductView.as_view(), name='add-product'),
    path('add-admin', views.AddAdminView.as_view(), name='add-admin'),
    path('modify-product', views.ModifyProductStockView.as_view(), name='modify-product'),
    path('statistics', views.StatisticsView.as_view(), name='statistics'),

    
    
]
