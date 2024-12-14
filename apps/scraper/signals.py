from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ScrapingProcess, Product, License, PageScreenshot, ThumbnailImage, Image
from django.utils import timezone
from .models import Product
from apps.ai.models import ProductAIVersion



# models.py (or signals.py)


# @receiver(post_save, sender=ScrapingProcess)
# def process_scraped_products(sender, instance, created, **kwargs):
#     """
#     This signal is triggered when a ScrapingProcess is saved.
#     If the status is changed to 'completed', it will trigger product fetching logic.
#     """
#     # Check if the process was not just created and is marked as 'completed'
#     if instance.status == 'pending' and instance.source_websites:
#         # Get the current time (when the scraping completed)
#         completion_time = timezone.now()

#         # Example: Fetch or process products related to the ScrapingProcess
#         print(f"Scraping Process {instance.id} completed at {completion_time}.")

#         # Placeholder logic for fetching products
#         # You might want to add your scraping function here
#         fetch_products(instance)

#         print(f"Products processed for ScrapingProcess {instance.id}.")



