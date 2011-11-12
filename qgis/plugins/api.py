from rpc4django import rpcmethod
from plugins.models import *
from validator import validator
from django.contrib.auth.decorators import login_required, user_passes_test


# Decorator
staff_required = user_passes_test(lambda u: u.is_staff)

@staff_required
@rpcmethod(name='plugin.upload', signature=['struct', 'string'])
def plugin_upload(package):
    """
    Accepts a base64encoded zip file.
    """
    try:
        cleaned_data = validator(package)
    except ValidationError, e:
        msg = unicode(_('File upload must be a valid QGIS Python plugin compressed archive.'))
        raise ValidationError("%s %s" % (msg, ','.join(e.messages)))

    import ipy; ipy.shell()
    return True