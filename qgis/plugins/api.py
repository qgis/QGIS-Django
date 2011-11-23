from rpc4django import rpcmethod
from xmlrpclib import Fault
from plugins.models import *
from validator import validator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import IntegrityError
from plugins.views import plugin_notify
import StringIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

# Transaction
from django.db import connection



@rpcmethod(name='plugin.upload', signature=['struct', 'binary'], permission='plugins.add_plugin')
def plugin_upload(package, **kwargs):
    """
    Creates a new plugin or updates an existing one
    """

    try:
        request = kwargs.get('request')
        package = StringIO.StringIO(package.data)
        try:
            cleaned_data = dict(validator(package))
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

        # Gets existing plugin
        try:
            plugin = Plugin.objects.get(package_name=plugin_data['package_name'])
            # Apply new values
            plugin.name         = plugin_data['name']
            plugin.description  = plugin_data['description']
            plugin.icon         = plugin_data['icon']
            is_new = False
        except Plugin.DoesNotExists:
            plugin = Plugin(**plugin_data)
            is_new = True

        # Optional Metadata:
        if cleaned_data.get('homepage'):
            plugin.homepage = cleaned_data.get('homepage')
        if cleaned_data.get('tracker'):
            plugin.tracker = cleaned_data.get('tracker')
        if cleaned_data.get('repository'):
            plugin.repository = cleaned_data.get('repository')

        plugin.save()

        if is_new:
            plugin_notify(plugin)

        # Takes care of tags
        if cleaned_data.get('tags'):
            plugin.tags.set(*cleaned_data.get('tags').split(','))

        #import ipy; ipy.shell()

        version_data =  {
            'plugin'            : plugin,
            'min_qg_version'    : cleaned_data['qgisMinimumVersion'],
            'version'           : cleaned_data['version'],
            'created_by'        : request.user,
            'package'           : InMemoryUploadedFile(package, 'package',
                                    "%s.zip" % plugin.package_name, 'application/zip',
                                    package.len, 'UTF-8'),
            'approved'          : request.user.has_perm('plugins.can_approve'),
            'experimental'      : getattr(cleaned_data, 'experimental', False),
        }
        new_version = PluginVersion(**version_data)
        new_version.save()
    except IntegrityError:
        # Avoids error: current transaction is aborted, commands ignored until
        # end of transaction block
        connection.close()
        raise

    return (plugin.pk, new_version.pk)