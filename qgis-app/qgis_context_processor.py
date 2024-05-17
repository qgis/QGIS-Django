from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def additions(request):
    """Insert some additional information into the template context
    from the settings and set the base template according to qs.
    """
    if is_ajax(request=request) or request.GET.get("ajax"):
        base_template = "ajax_base.html"
        is_naked = True
    else:
        base_template = "base.html"
        is_naked = False

    additions = {
        "BASE_TEMPLATE": base_template,
        "IS_NAKED": is_naked,
        "DEBUG": settings.DEBUG,
    }

    return additions
