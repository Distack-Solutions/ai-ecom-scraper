from django.contrib import admin
from .models import ProductAIVersion, OpenAIAPIUsage

# Registering ProductAIVersion in the AI app
admin.site.register(ProductAIVersion)
admin.site.register(OpenAIAPIUsage)