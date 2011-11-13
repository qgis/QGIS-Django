from rpc4django import rpcmethod
from plugins.models import *
from validator import validator
from django.contrib.auth.decorators import login_required, user_passes_test
from plugins.views import plugin_notify

from django.core.exceptions import ValidationError


@rpcmethod(name='plugin.upload', signature=['struct', 'binary'], permission='plugins.add_plugin')
def plugin_upload(package, **kwargs):
    """
    Creates a new plugin
    """
    request = kwargs.get('request')
    import ipy; ipy.shell()
    try:
        cleaned_data = validator(package)
    except ValidationError, e:
        msg = unicode(_('File upload must be a valid QGIS Python plugin compressed archive.'))
        raise ValidationError("%s %s" % (msg, ','.join(e.messages)))

    plugin_data = {
        'name'              : form.cleaned_data['name'],
        'package_name'      : form.cleaned_data['package_name'],
        'description'       : form.cleaned_data['description'],
        'created_by'        : request.user,
        'icon'              : form.cleaned_data['icon_file'],
    }
    new_plugin = Plugin(**plugin_data)
    new_plugin.save()
    plugin_notify(new_plugin)

    version_data =  {
        'plugin'            : new_plugin,
        'min_qg_version'    : form.cleaned_data['qgisMinimumVersion'],
        'version'           : form.cleaned_data['version'],
        'created_by'        : request.user,
        'package'           : form.cleaned_data['package'],
        'approved'          : request.user.has_perm('plugins.can_approve'),
        'experimental'      : form.cleaned_data['experimental'],
    }
    new_version = PluginVersion(**version_data)
    new_version.save()
    return (plugin.pk, new_version.pk)