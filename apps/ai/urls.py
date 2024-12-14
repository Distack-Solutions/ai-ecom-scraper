from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    # Other URLs here...
    path('update-product-ai-details/<int:product_id>/', views.update_ai_details, name='update_ai_details'),
    path('rengenerate-product-details/<int:product_id>/', views.regenerate_ai, name='regenerate_ai'),

]
