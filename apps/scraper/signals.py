from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import ScrapingProcess, Product, License, PageScreenshot, ThumbnailImage, Image
from django.utils import timezone
from .models import Product
from apps.ai.models import ProductAIVersion
from apps.scraper.libs.wc import WooCommerceManager
from django.db.models.signals import pre_save
from django.db import models
# models.py (or signals.py)


@receiver(post_save, sender=Product)
def upload_product_to_wc(sender, instance, created, **kwargs):
    # Check if the process was not just created and is marked as 'completed'
    if instance.status == 'published' and hasattr(instance, 'ai_version'):
        # upload to wc
        # 
        print("Publishing on wc...")


@receiver(pre_save, sender=Product)
def assign_model_id(sender, instance, **kwargs):
    if not instance.model_id:  # Only assign if not already set
        max_model_id = Product.objects.aggregate(models.Max('model_id'))['model_id__max'] or 399
        instance.model_id = max_model_id + 1

@receiver(pre_save, sender=Product)
def assign_model_url(sender, instance, **kwargs):
    if not instance.model_url:
        instance.model_url = instance.get_website_url()