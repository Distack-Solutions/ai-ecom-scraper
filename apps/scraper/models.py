from django.db import models
from django.contrib.auth.models import User



# python manage.py makemigrations
# python manage.py migrate


class SourceWebsite(models.Model):
    name = models.CharField(max_length=255, verbose_name="Website Name")
    logo = models.ImageField(upload_to='website_logos/', verbose_name="Website Logo")
    script_name = models.CharField(max_length=255, verbose_name="Scraper Script Name")
    url = models.URLField(max_length=255, verbose_name="Website URL")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Source Website"
        verbose_name_plural = "Source Websites"


class Criteria(models.Model):
    TYPE_CHOICES = [
        ('equals', 'Equals'),
        ('less_than', 'Less Than'),
        ('greater_than', 'Greater Than'),
        ('not', 'Not'),
    ]

    name = models.CharField(max_length=255, verbose_name="Criteria Name")
    key = models.CharField(max_length=255, verbose_name="Criteria Key")
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type")
    value = models.CharField(max_length=255, verbose_name="Value")
    is_required = models.BooleanField(default=False, verbose_name="Is Required")

    def __str__(self):
        return f"{self.name} ({self.type})"

    class Meta:
        verbose_name = "Criteria"
        verbose_name_plural = "Criterias"



class ScrapingProcess(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    search_query = models.CharField(max_length=255, verbose_name="Search Query")
    source_websites = models.ManyToManyField(SourceWebsite, verbose_name="Source Websites")
    criterias = models.ManyToManyField(Criteria, null=True, blank=True, verbose_name="Criterias")
    max_records = models.PositiveIntegerField(default=0, verbose_name="Max Records")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Status")
    started_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Started By")
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Started At")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completed At")

    def __str__(self):
        return f"Scraping {self.search_query} by {self.started_by}"

    class Meta:
        verbose_name = "Scraping Process"
        verbose_name_plural = "Scraping Processes"


class PageScreenshot(models.Model):
    image = models.ImageField(upload_to="page-screenshot", null=True, blank=True)
    url = models.URLField(null=True, blank=True)

class License(models.Model):
    json = models.JSONField(null=True, blank=True)


class ThumbnailImage(models.Model):
    image = models.ImageField(upload_to='thumbnail_images/', null=True, blank=True, verbose_name="Thumbnail Image")
    url = models.URLField(null=True, blank=True, verbose_name="Thumbnail URL")
    
    def __str__(self):
        return self.url if self.url else f"Image: {self.image.name}" if self.image else "No Thumbnail"

    class Meta:
        verbose_name = "Thumbnail Image"
        verbose_name_plural = "Thumbnail Images"


class Product(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    sku = models.CharField(max_length=50, unique=True, null=True, blank=True)
    scraped_by = models.ForeignKey(ScrapingProcess, on_delete=models.CASCADE, verbose_name="Scraped By")
    title = models.CharField(max_length=255, verbose_name="Product Title")
    category = models.CharField(max_length=255, null=True, blank=True, verbose_name="Category")
    description = models.TextField(verbose_name="Description")
    thumbnail = models.OneToOneField(ThumbnailImage, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Thumbnail")
    source_website = models.ForeignKey(SourceWebsite, on_delete=models.CASCADE, verbose_name="Source Website")
    is_published = models.BooleanField(default=False, verbose_name="Is Published")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Status")
    license = models.OneToOneField(License, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Product License")
    page_screenshot = models.OneToOneField(PageScreenshot, on_delete=models.SET_NULL, verbose_name="Page Screenshot", null=True, blank=True)
    is_commercial_allowed = models.BooleanField(default=False, verbose_name="Is Commercial Allowed")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    def populate_printables_data(self, products):
        for product in products:
            print(product)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"



class Image(models.Model):
    image_url = models.URLField(null=True, blank=True)
    image_file = models.ImageField(null=True, blank=True, upload_to='product_images/', verbose_name="Image File")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name="Product")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Image"
        verbose_name_plural = "Images"



