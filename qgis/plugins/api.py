from rpc4django import rpcmethod
from plugins.models import *
from validator import validator
from django.contrib.auth.decorators import login_required, user_passes_test
from plugins.views import plugin_notify
import StringIO

from django.core.exceptions import ValidationError



@rpcmethod(name='plugin.auth_test', signature=['int'], permission='plugins.add_plugin')
def plugin_auth_test(**kwargs):
    """
    Test for LDAP auth
    """
    return 1



@rpcmethod(name='plugin.upload', signature=['struct', 'binary'], permission='plugins.add_plugin')
def plugin_upload(package, **kwargs):
    """
    Creates a new plugin
    """
    request = kwargs.get('request')
    try:
        import ipy; ipy.shell()
        cleaned_data = validator(StringIO.StringIO(package.data))
    except ValidationError, e:
        msg = unicode(_('File upload must be a valid QGIS Python plugin compressed archive.'))
        raise ValidationError("%s %s" % (msg, ','.join(e.messages)))

    plugin_data = {
        'name'              : cleaned_data['name'],
        'package_name'      : cleaned_data['package_name'],
        'description'       : cleaned_data['description'],
        'created_by'        : request.user,
        'icon'              : cleaned_data['icon_file'],
    }

    # Optional Metadata:
    if cleaned_data.get('homepage'):
        plugin_data.homepage = cleaned_data.get('homepage')
    if cleaned_data.get('tracker'):
        plugin_data.tracker = cleaned_data.get('tracker')
    if cleaned_data.get('repository'):
        plugin_data.repository = cleaned_data.get('repository')


    new_plugin = Plugin(**plugin_data)
    new_plugin.save()
    plugin_notify(new_plugin)

    version_data =  {
        'plugin'            : new_plugin,
        'min_qg_version'    : cleaned_data['qgisMinimumVersion'],
        'version'           : cleaned_data['version'],
        'created_by'        : request.user,
        'package'           : cleaned_data['package'],
        'approved'          : user.has_perm('plugins.can_approve'),
        'experimental'      : cleaned_data['experimental'],
    }
    new_version = PluginVersion(**version_data)
    new_version.save()
    return (plugin.pk, new_version.pk)