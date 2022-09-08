from django.conf import settings
from django.core.files.storage import default_storage
from django.template import Library

register = Library()


@register.filter
def avatar_exists(value):
    """
    Test if an avatar exists
    """
    default_storage.exists("%simg/faces/%s.png" % (settings.MEDIA_ROOT, value))
