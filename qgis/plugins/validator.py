"""
Plugin validator class

"""
import zipfile
import mimetypes
import re
import os

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.forms import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

PLUGIN_MAX_UPLOAD_SIZE= getattr(settings, 'PLUGIN_MAX_UPLOAD_SIZE', 1048576)

def validator(package):
    """
    Analyzes a zipped file, returns metadata if success, False otherwise.
    If the new icon metadata is found, an inmemory file object is also returned

    Current checks:

        * size <= PLUGIN_MAX_UPLOAD_SIZE
        * zip contains __init__.py in first level dir
        * mandatory metadata: ('name', 'description', 'version', 'qgisMinimumVersion')

    """

    if package.size > PLUGIN_MAX_UPLOAD_SIZE:
        raise ValidationError( _("File is too big. Max size is %s Bytes") % PLUGIN_MAX_UPLOAD_SIZE )

    if False and package.content_type != 'application/zip':
        raise forms.ValidationError( msg )
    else:
        try:
            zip = zipfile.ZipFile( package )
        except:
            raise ValidationError( _("Could not unzip file.") )
        for zname in zip.namelist():
            if zname.find('..') != -1 or zname.find(os.path.sep) == 0 :
                raise ValidationError( _("For security reasons, zip file cannot contain path informations") )
        bad_file = zip.testzip()
        if bad_file:
            zip.close()
            del zip
            raise ValidationError( msg )

        # Checks that package_name/__init__.py exists
        namelist = zip.namelist()
        package_name = namelist[0]
        initname = package_name + '__init__.py'
        # Cuts the trailing slash
        package_name = package_name[:-1]
        if not initname in namelist:
            raise ValidationError(_('Cannot find __init__.py in the compressed package: this does not seems a valid plugin (I searched for %s)') % initname)

        # Checks metadata
        initcontent = zip.read(initname)

        # Ugly RE: regexp guru wanted!
        metadata = re.findall('def\s+([^c]\w+).*?return\s+["\'](.*?)["\']', initcontent , re.DOTALL)
        if not metadata:
            raise ValidationError(_('Cannot find valid metadata in %s') % initname)

        for md in ('name', 'description', 'version', 'qgisMinimumVersion'):
            if not md in dict(metadata) or not dict(metadata)[md]:
                raise ValidationError(_('Cannot find metadata %s') % md)

        # Process Icon
        try:
            icon = zip.open(package_name + '/' + dict(metadata)['icon'])
            icon_file = SimpleUploadedFile(dict(metadata)['icon'], icon.read(), mimetypes.guess_type(dict(metadata)['icon']))
        except:
            icon_file = None

        metadata.append(('icon_file', icon_file))

        zip.close()
        del zip
        # Adds package_name
        metadata.append(('package_name', package_name))
    return metadata

