from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.scraper.models import ScrapingProcess, Product
from django.utils import timezone
from .models import ProductAIVersion


# models.py (or signals.py)

@receiver(post_save, sender=Product)
def create_ai_version(sender, instance, created, **kwargs):
    # Check if the product is approved and doesn't already have an AI version
    if instance.status == 'approved' and not hasattr(instance, 'ai_version'):
        ai_details = instance.generate_ai_details()
        ai_object = instance.create_or_update(ai_details)