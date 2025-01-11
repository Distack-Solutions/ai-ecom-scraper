# custom_filters.py
from django import template
from django.utils.html import format_html
import base64

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='get_boolean')
def get_boolean(value):
    if value:
        return format_html('<span class="text-center">&#x2713;</span>')
    return format_html('<span class="text-center">&#x2717;</span>')

@register.filter(name='b64encode')
def b64encode(value):
    return base64.b64encode(value).decode('utf-8')