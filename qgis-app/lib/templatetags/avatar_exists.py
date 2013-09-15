from django.template import Library
from django.core.files.storage import default_storage
from django.conf import settings

register = Library()

@register.filter
def avatar_exists( value ):
    """
    Test if an avatar exists
    """
    path = '%simg/faces/%s.png' % (settings.MEDIA_ROOT, value)
    print path
    default_storage.exists(path)
