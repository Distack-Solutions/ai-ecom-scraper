from django.urls import path
from . import views
from django.views.i18n import set_language

app_name = "scraper"

urlpatterns = [
    # path('jobs', views.all_jobs, name='job_home'),
    path('products/', views.all_products, name='products'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),  # Add this line    
    path('products/<int:product_id>/approve', views.approve_product, name='approve-product'),    
    path('products/<int:product_id>/approve-ajax', views.approve_product_via_ajax, name='approve-product-ajax'),
    path('products/<int:product_id>/decline', views.decline_product, name='decline-product'),
    path('products/<int:product_id>/delete', views.delete_product, name='delete-product'),
    
    path('products/<int:product_id>/screenshot/', views.view_screenshot, name='view_screenshot'),

    path('processes/initiate/', views.initiate_process, name='initiate-process'),
    path('processes/', views.processes_list, name='processes'),

    path('ajax/wc/publish-products', views.ajax_upload_product_to_wc, name='upload-wc-product'),

    path('ajax/products/operation', views.process_products_operation, name='process-products-operation'),

    path('ajax/products/operation/sse', views.process_products_sse, name='process-products-sse'),

    path('ajax/products/scraping/sse', views.initiate_scraping_process, name='scrape-products-sse'),

    path('logs/', views.logs_view, name='logs-view'),

]
