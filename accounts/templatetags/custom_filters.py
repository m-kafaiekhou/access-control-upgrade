from django import template
import json

register = template.Library()

@register.filter
def any_true(data):
    if any(value for value in data.values() if value):
        return "دارد"
    return "ندارد"
