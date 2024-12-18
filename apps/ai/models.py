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

    def get_images(self):
        images = self.product.images.all()
        wc_images = []
        i = 1

        if self.product.thumbnail:
            thumbnail_url = None
            if self.product.thumbnail.url:
                thumbnail_url = self.product.thumbnail.url

            if self.product.thumbnail.image.url:
                thumbnail_url = self.product.thumbnail.image.url

            if thumbnail_url:
                wc_images.append({
                    'name': f"{self.product.title} - Thumbnail",
                    'src': thumbnail_url
                })

        for image in images:
            image_url = None
            image_name = f'{self.product.title} - Gallery image {i}'
            if image.image_file:
                image_url = image.image_file.url
            else:
                image_url = image.image_url

            wc_images.append(
                {
                    'name': image_name,
                    'src': image_url
                })
            i+=1

        return wc_images

    def __str__(self):
        return f"AI Version of {self.product.title}"

    class Meta:
        verbose_name = "Product AI Version"
        verbose_name_plural = "Product AI Versions"
