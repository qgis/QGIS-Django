"""
XML-RPC webservices for the plugin web application
"""

from rpc4django import rpcmethod
from xmlrpclib import Fault
from plugins.models import *
from validator import validator
from django.db import IntegrityError
from plugins.views import plugin_notify
import StringIO
from taggit.models import Tag

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.files.uploadedfile import InMemoryUploadedFile

# Transaction
from django.db import connection

@rpcmethod(name='plugin.upload', signature=['array', 'base64'], login_required=True)
def plugin_upload(package, **kwargs):
    """

    Creates a new plugin or updates an existing one

    Returns an array containing the ID (primary key) of the plugin and the ID of the version.

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
        except Plugin.DoesNotExist:
            plugin = Plugin(**plugin_data)
            is_new = True

        # Optional Metadata:
        if cleaned_data.get('homepage'):
            plugin.homepage = cleaned_data.get('homepage')
        if cleaned_data.get('tracker'):
            plugin.tracker = cleaned_data.get('tracker')
        if cleaned_data.get('repository'):
            plugin.repository = cleaned_data.get('repository')
        if cleaned_data.get('deprecated'):
            plugin.deprecated = cleaned_data.get('deprecated')

        plugin.save()

        if is_new:
            plugin_notify(plugin)

        # Takes care of tags
        if cleaned_data.get('tags'):
            plugin.tags.set(*cleaned_data.get('tags').split(','))

        version_data =  {
            'plugin'            : plugin,
            'min_qg_version'    : cleaned_data['qgisMinimumVersion'],
            'version'           : cleaned_data['version'],
            'created_by'        : request.user,
            'package'           : InMemoryUploadedFile(package, 'package',
                                    "%s.zip" % plugin.package_name, 'application/zip',
                                    package.len, 'UTF-8'),
            'approved'          : request.user.has_perm('plugins.can_approve') or plugin.approved,
        }

        # Optional version metadata
        if cleaned_data.get('experimental'):
            version_data['experimental'] = cleaned_data.get('experimental')
        if cleaned_data.get('changelog'):
            version_data['changelog'] = cleaned_data.get('changelog')

        new_version = PluginVersion(**version_data)
        new_version.save()
    except IntegrityError:
        # Avoids error: current transaction is aborted, commands ignored until
        # end of transaction block
        connection.close()
        raise

    return (plugin.pk, new_version.pk)


@rpcmethod(name='plugin.tags', signature=['array'], login_required=False)
def plugin_tags(**kwargs):
    """
    Returns a list of current tags, in alphabetical order
    """
    return [t.name for t in Tag.objects.all().order_by('name')]
 

@rpcmethod(name='plugin.vote', signature=['array', 'integer', 'integer'], login_required=False)
def plugin_tags(plugin_id, vote, **kwargs):
    """
    Vote a plugin, valid values are 1-5
    """
    try:
        request = kwargs.get('request')
    except:
        msg = unicode(_('Invalid request.'))
        raise ValidationError(msg)
    try:
        plugin = Plugin.objects.get(pk=plugin_id)
    except Plugin.DoesNotExist:
        msg = unicode(_('Plugin with id %s does not exists.') % plugin_id)
        raise ValidationError(msg)
    if not int(vote) in range(1, 6):
        msg = unicode(_('%s is not a valid vote (1-5).') % vote)
        raise ValidationError(msg)
    return [plugin.rating.add(score=int(vote), user=request.user, ip_address=request.META['REMOTE_ADDR'])]
 
