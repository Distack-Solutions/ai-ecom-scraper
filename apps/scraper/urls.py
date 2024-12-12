from django.urls import path
from . import views
from django.views.i18n import set_language

app_name = "scraper"

urlpatterns = [
    # path('jobs', views.all_jobs, name='job_home'),
    path('products/', views.all_products, name='products'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),  # Add this line
    path('products/<int:product_id>/delete', views.delete_product, name='delete-product'),  # Add this line
    path('products/<int:product_id>/screenshot/', views.view_screenshot, name='view_screenshot'),

    path('processes/initiate/', views.initiate_process, name='initiate-process'),
    path('processes/', views.processes_list, name='processes')


]
