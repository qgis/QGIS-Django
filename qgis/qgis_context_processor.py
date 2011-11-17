from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
import re

def additions(request):
    """Insert some additional information into the template context
    from the settings and set the base template according to qs.
    """
    if request.is_ajax() or request.GET.get('ajax'):
        base_template = 'ajax_base.html'
    else:
        base_template = 'base.html'

    additions = {
        'BASE_TEMPLATE': base_template,
        'DEBUG': settings.DEBUG,
    }

    return additions
