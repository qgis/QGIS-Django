"""
Plugin validator class

"""
import zipfile
import tempfile
import re, os
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.forms import ValidationError

PLUGIN_MAX_UPLOAD_SIZE= getattr(settings, 'PLUGIN_MAX_UPLOAD_SIZE', 1048576)



def validator(package):
    """
    Analyze a zipped file, returns metadata if success, False otherwise.

    Current checks:

        * size <= PLUGIN_MAX_UPLOAD_SIZE
        * zip contains __init__.py in first level dir

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
                raise ValidationError( _("For security reasons, zip file cannot contains path informations") )
        bad_file = zip.testzip()
        if bad_file:
            zip.close()
            del zip
            raise ValidationError( msg )

        # check that Dirname/__init__.py exists
        namelist = zip.namelist()
        dirname = namelist[0]
        initname = dirname + '__init__.py'
        if not initname in namelist:
            raise ValidationError(_('Cannot find __init__.py in the compressed package: this does not seems a valid plugin (I searched for %s)') % initname)

        # Check metadata
        initcontent = zip.read(initname)
        metadata = re.findall('def\s+(\w+).*?return\s+["\'](.*?)["\']', initcontent , re.DOTALL)
        if not metadata:
            raise ValidationError(_('Cannot find valid metadata in %s') % initname)

        for md in ('name', 'description', 'version', 'qgisMinimumVersion'):
            if not md in dict(metadata) or not dict(metadata)[md]:
                raise ValidationError(_('Cannot find metadata %s') % md)
        zip.close()
        del zip
    return metadata

