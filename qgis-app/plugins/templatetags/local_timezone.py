import pytz
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="local_timezone", is_safe=True)
def local_timezone(date, args="LONG"):
    try:
        utcdate = date.astimezone(pytz.utc).isoformat()
        if args and str(args) == "SHORT":
            result = '<span class="user-timezone-short">%s</span>' % (utcdate,)
        elif args and str(args) == "SHORT_NATURAL_DAY":
            result = '<span class="user-timezone-short-naturalday">%s</span>' % (utcdate,)
        elif  args and str(args) == "WITH-UTC":
            result = utcdate
        else:
            result = '<span class="user-timezone">%s</span>' % (utcdate,)
    except AttributeError:
        result = date
    return mark_safe(result)
