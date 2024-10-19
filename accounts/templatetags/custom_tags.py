from django import template
from ..models import OperatorLog

register = template.Library()

@register.simple_tag
def get_last_log(operator):
    last_log = OperatorLog.objects.filter(operator=operator).last()
    return last_log