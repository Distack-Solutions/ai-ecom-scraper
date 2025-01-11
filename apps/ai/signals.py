from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.scraper.models import ScrapingProcess, Product
from django.utils import timezone
from .models import ProductAIVersion


# models.py (or signals.py)

