# In your app's templatetags directory (e.g., myapp/templatetags/math_filters.py)
from django import template

register = template.Library()

@register.filter(name='multiply')
def multiply(value, arg):
    return value * arg

@register.filter(name='subtract')
def subtract(value, arg):
    return value - arg

@register.filter(name='divide')
def divide(value, arg):
    return value / arg