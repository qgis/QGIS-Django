import re
from zipfile import ZipFile
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def extract_file(file, file_type):
    """Extract the zipfile and return the file with same type"""
    try:
        zip_file = ZipFile(file)
    except Exception:
        raise ValidationError(_("Could not unzip file."))

    file_path = ''
    file_size = 0
    rgx = r'.*\.{}$'.format(file_type)
    for file in zip_file.filelist:
        find_wavefront = re.findall(rgx, file.filename)
        if find_wavefront and find_wavefront[0]:
            file_path = find_wavefront[0]
            file_size = file.file_size
    return (file_path, file_size)


def get_obj_info(file):
    """Extract the wavefront zipfile and return the obj info."""
    obj_path, obj_filesize = extract_file(file, 'obj')
    return obj_path, obj_filesize


def get_mtl_info(file):
    """Extract the wavefront zipfile and return the mtl info."""
    obj_path, obj_filesize = extract_file(file, 'mtl')
    return obj_path, obj_filesize

