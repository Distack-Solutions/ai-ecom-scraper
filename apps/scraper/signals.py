from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ScrapingProcess, Product, License, PageScreenshot, ThumbnailImage, Image
from django.utils import timezone
from .models import Product
from apps.ai.models import ProductAIVersion
from apps.scraper.libs.wc import WooCommerceManager


# models.py (or signals.py)


@receiver(post_save, sender=Product)
def upload_product_to_wc(sender, instance, created, **kwargs):
    # Check if the process was not just created and is marked as 'completed'
    if instance.status == 'published' and hasattr(instance, 'ai_version'):
        # upload to wc
        # 
        print("Publishing on wc...")

