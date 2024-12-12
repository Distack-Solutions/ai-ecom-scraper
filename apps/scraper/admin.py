from django.contrib import admin
from .models import SourceWebsite, Criteria, ScrapingProcess, Product, Image, PageScreenshot

# Registering models with basic admin panel display
admin.site.register(SourceWebsite)
admin.site.register(Criteria)
admin.site.register(ScrapingProcess)
admin.site.register(Product)
admin.site.register(Image)
admin.site.register(PageScreenshot)
