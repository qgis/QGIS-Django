import re
from zipfile import ZipFile
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def get_obj_info(file):
    """Extract the wavefront zipfile and return the obj info."""
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
