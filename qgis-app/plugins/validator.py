"""
Plugin validator class

"""
import zipfile
import mimetypes
import re
import os
import ConfigParser
import StringIO
import codecs
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.forms import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile


PLUGIN_MAX_UPLOAD_SIZE=getattr(settings, 'PLUGIN_MAX_UPLOAD_SIZE', 1048576)
PLUGIN_REQUIRED_METADATA=getattr(settings, 'PLUGIN_REQUIRED_METADATA', ('name', 'description', 'version', 'qgisMinimumVersion', 'author', 'email'))

PLUGIN_OPTIONAL_METADATA=getattr(settings, 'PLUGIN_OPTIONAL_METADATA', ('homepage', 'changelog', 'tracker', 'qgisMaximumVersion', 'repository', 'tags', 'deprecated', 'experimental'))
PLUGIN_BOOLEAN_METADATA=getattr(settings, 'PLUGIN_BOOLEAN_METADATA', ('experimental', 'deprecated'))


def _read_from_init2(initcontent, initname):
    """
    Read metadata from __init__.py, raise ValidationError
    """
    metadata = []
    i=0
    lines=initcontent.split('\n')
    while i < len(lines):
        if re.search('def\s+([^\(]+)', lines[i]):
            k=re.search('def\s+([^\(]+)', lines[i]).groups()[0]
            i+=1
            while i < len(lines) and lines[i] != '':
                if re.search('return\s+["\']?([^"\']+)["\']?', lines[i]):
                    metadata.append((k, re.search('return\s+["\']?([^"\']+)["\']?', lines[i]).groups()[0]))
                    break
                i+=1
        i+=1
    if not len(metadata):
        raise ValidationError(_('Cannot find valid metadata in %s') % initname)
    return metadata

def _read_from_init(initcontent, initname):
    """
    Read metadata from __init__.py, raise ValidationError
    DEPRECATED: _read_from_init2 has better support for metadata
    """
    metadata = []
    metadata.extend(re.findall('def\s+([^c]\w+).*?return\s+.*?(?P<quote>["\'])(.*?)(?P=quote)', initcontent , re.DOTALL))
    if not metadata:
        raise ValidationError(_('Cannot find valid metadata in %s') % initname)
    return [(md[0], md[2]) for md in metadata]

def _check_required_metadata(metadata):
    """
    Checks if required metadata are in place, raise ValidationError if not found
    """
    for md in PLUGIN_REQUIRED_METADATA:
        if not md in dict(metadata) or not dict(metadata)[md]:
            raise ValidationError(_('Cannot find metadata <strong>%s</strong> in metadata source (%s).<br />Please bear in mind that the current implementation of the <tt>__init__.py</tt> validator is based on regular expressions, check that your metadata functions directly return metadata values as strings.<br />For further informations about metadata parsing in this application, please see: <a target="_blank"  href="https://github.com/qgis/QGIS-Documentation/blob/master/source/docs/pyqgis_developer_cookbook/13_plugins.rst#plugin-metadata">metadata documentation</a>') % (md, dict(metadata).get('metadata_source')))


def validator(package):
    """
    Analyzes a zipped file, returns metadata if success, False otherwise.
    If the new icon metadata is found, an inmemory file object is also returned

    Current checks:

        * size <= PLUGIN_MAX_UPLOAD_SIZE
        * zip contains __init__.py in first level dir
        * mandatory metadata: ('name', 'description', 'version', 'qgisMinimumVersion', 'author', 'email')
        * package_name regexp: [A-Za-z][A-Za-z0-9-_]+
        * author regexp: [^/]+

    """
    try:
        if package.size > PLUGIN_MAX_UPLOAD_SIZE:
            raise ValidationError( _("File is too big. Max size is %s Bytes") % PLUGIN_MAX_UPLOAD_SIZE )
    except AttributeError:
        if package.len  > PLUGIN_MAX_UPLOAD_SIZE:
            raise ValidationError( _("File is too big. Max size is %s Bytes") % PLUGIN_MAX_UPLOAD_SIZE )

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

    # Checks that package_name  exists
    namelist = zip.namelist()
    try:
        package_name = namelist[0][:namelist[0].index('/')]
    except:
        raise ValidationError( _("Cannot find a folder inside the compressed package: this does not seems a valid plugin") )

    # Cuts the trailing slash
    if package_name.endswith('/'):
        package_name = package_name[:-1]
    initname = package_name + '/__init__.py'
    metadataname = package_name + '/metadata.txt'
    if not initname in namelist and not metadataname in namelist:
        raise ValidationError(_('Cannot find __init__.py or metadata.txt in the compressed package: this does not seems a valid plugin (I searched for %s and %s)') % (initname, metadataname))

    # Checks for __init__.py presence
    if not initname in namelist:
        raise ValidationError(_("Cannot find __init__.py in plugin package."))

    # Checks metadata
    metadata = []
    # First parse metadata.txt
    if metadataname in namelist:
        try:
            parser = ConfigParser.ConfigParser()
            parser.optionxform = str
            parser.readfp(StringIO.StringIO(codecs.decode(zip.read(metadataname), "utf8")))
            if not parser.has_section('general'):
                raise ValidationError(_("Cannot find a section named 'general' in %s") % metadataname)
            metadata.extend(parser.items('general'))
        except Exception, e:
            raise ValidationError(_("Errors parsing %s. %s") % (metadataname, e))
        metadata.append(('metadata_source', 'metadata.txt'))
    else:
        # Then parse __init__
        # Ugly RE: regexp guru wanted!
        initcontent = zip.read(initname)
        metadata.extend(_read_from_init2(initcontent, initname))
        if not metadata:
            raise ValidationError(_('Cannot find valid metadata in %s') % initname)
        metadata.append(('metadata_source', '__init__.py'))

    _check_required_metadata(metadata)

    # Process Icon
    try:
        # Strip leading dir for ccrook plugins
        if dict(metadata)['icon'].startswith('./'):
            icon_path = dict(metadata)['icon'][2:]
        else:
            icon_path = dict(metadata)['icon']
        icon = zip.read(package_name + '/' + icon_path)
        icon_file = SimpleUploadedFile(dict(metadata)['icon'], icon, mimetypes.guess_type(dict(metadata)['icon']))
    except:
        icon_file = None

    metadata.append(('icon_file', icon_file))

    # Transforms booleans flags (experimental)
    for flag in PLUGIN_BOOLEAN_METADATA:
        if flag in dict(metadata):
            metadata[metadata.index((flag, dict(metadata)[flag]))] = (flag, dict(metadata)[flag].lower() == 'true' or dict(metadata)[flag].lower() == '1')

    # Adds package_name
    if not re.match(r'^[A-Za-z][A-Za-z0-9-_]+$', package_name):
        raise ValidationError(_("Package name must start with an ASCII letter and can contain ASCII letters, digits and the signs '-' and '_'."))
    metadata.append(('package_name', package_name))

    # Last temporary rule, check if mandatory metadata are also in __init__.py
    # fails if it is not
    min_qgs_version = dict(metadata).get('qgisMinimumVersion')
    max_qgs_version = dict(metadata).get('qgisMaximumVersion')
    if tuple(min_qgs_version.split('.')) < tuple('1.8'.split('.')) and metadataname in namelist:
        initcontent = zip.read(initname)
        try:
            initmetadata = _read_from_init2(initcontent, initname)
            initmetadata.append(('metadata_source', '__init__.py'))
            _check_required_metadata(initmetadata)
        except ValidationError, e:
            raise ValidationError(_("qgisMinimumVersion is set to less than  1.8 (%s) and there were errors reading metadata from the __init__.py file. This can lead to errors in versions of QGIS less than 1.8, please either set the qgisMinimumVersion to 1.8 or specify the metadata also in the __init__.py file. Reported error was: %s") % (min_qgs_version, ','.join(e.messages)))

    zip.close()
    del zip

    # Check author
    if 'author' in dict(metadata):
        if not re.match(r'^[^/]+$', dict(metadata)['author']):
           raise ValidationError(_("Author name cannot contain slashes."))

    # strip and check
    checked_metadata = []
    for k,v in metadata:
        try:
            if not (k in PLUGIN_BOOLEAN_METADATA or k == 'icon_file'):
                #v.decode('UTF-8')
                checked_metadata.append((k, v.strip()))
            else:
                checked_metadata.append((k, v))
        except UnicodeDecodeError, e:
            raise ValidationError(_("There was an error converting metadata '%s' to UTF-8 . Reported error was: %s") % (k, e))


    return checked_metadata

