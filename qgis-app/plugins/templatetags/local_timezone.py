import pytz
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="local_timezone", is_safe=True)
def local_timezone(date):
    try:
        utcdate = date.astimezone(pytz.utc).isoformat()
        result = '<span class="user-timezone">%s</span>' % (utcdate, )
    except AttributeError:
        result = date
    return mark_safe(result)
