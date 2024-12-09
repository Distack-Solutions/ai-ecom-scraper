from django.db import models
from apps.scraper.models import Product

# python manage.py makemigrations
# python manage.py migrate

# Create your models here.
class ProductAIVersion(models.Model):
    title = models.CharField(max_length=255, verbose_name="AI Generated Title")
    expanded_description = models.TextField(verbose_name="Expanded Description")
    short_description = models.TextField(verbose_name="Short Description")
    meta_description = models.CharField(max_length=255, verbose_name="Meta Description")
    focus_keyphrase = models.CharField(max_length=255, verbose_name="Focus Keyphrase")
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="ai_version", verbose_name="Product")

    def __str__(self):
        return f"AI Version of {self.product.title}"

    class Meta:
        verbose_name = "Product AI Version"
        verbose_name_plural = "Product AI Versions"
