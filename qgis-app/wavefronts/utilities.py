import os.path
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

    obj_path = ''
    obj_filesize = 0
    rgx = r'.*\.obj$'
    for file in zip_file.filelist:
        find_wavefront = re.findall(rgx, file.filename)
        if find_wavefront and find_wavefront[0]:
            obj_path = find_wavefront[0]
            obj_filesize = file.file_size
    return (obj_path, obj_filesize)


def get_obj_info(file):
    """Extract the wavefront zipfile and return the obj info."""
    obj_path, obj_filesize = extract_file(file, 'obj')
    return obj_path, obj_filesize


def get_mtl_info(file):
    """Extract the wavefront zipfile and return the mtl info."""
    obj_path, obj_filesize = extract_file(file, 'mtl')
    filename, ext = os.path.splitext(obj_path)
    obj_path = f'{filename}.mtl'
    return obj_path, obj_filesize


# def get_obj_mtl_path(filepath):
#     # e.g /home/web/media/wavefronts/217fb6/odm_textured.dummy
#     path, filename = os.path.split(filepath)
#     for
