from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def star_rating(value):
    """Convert rating number to star display"""
    try:
        rating = int(value)
        return '★' * rating + '☆' * (5 - rating)
    except (ValueError, TypeError):
        return '☆☆☆☆☆'