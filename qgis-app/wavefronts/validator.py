"""Wavefront validator."""


import os
import pywavefront
import re
import shutil
import uuid
from zipfile import ZipFile
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _



class WavefrontValidator:

    def __init__(self, file):
        self.file = file

    def valid_zip(self):
        try:
            zip_file = ZipFile(self.file)
        except Exception as e:
            raise ValidationError(_("Could not unzip file."))
        return zip_file

    def get_wavefront_obj_path(self):
        rgx = r'.*\.obj$'
        for file in self.valid_zip().filelist:
            find_wavefront = re.findall(rgx, file.filename)
            if find_wavefront and find_wavefront[0]:
                # get the path of .obj file
                return find_wavefront[0]
        raise ValidationError(_('Could not find .obj file.'))

    def is_mtl_file_exist(self):
        obj_path = self.get_wavefront_obj_path()
        filename, ext = os.path.splitext(obj_path)
        mtl_file = f'{filename}.mtl'
        for file in self.valid_zip().filelist:
            if mtl_file == file.filename:
                return None
        raise ValidationError(_('Could not find .mtl file.'))

    def validate_wavefront(self):
        self.is_mtl_file_exist()
        obj_path = self.get_wavefront_obj_path()
        filename, ext = os.path.splitext(obj_path)
        mtl_path = f'{filename}.mtl'

        temp_dir = f'/tmp/{uuid.uuid4().hex[0:6]}'

        # create new directory for temporary file
        path, _ = os.path.split(obj_path)
        new_dir = f'{temp_dir}/{path}' if path else f'{temp_dir}'
        if not os.path.exists(new_dir):
            os.makedirs(new_dir)

        with open(f'{temp_dir}/{obj_path}', 'wb') as f:
            f.write(ZipFile(self.file).read(obj_path))
        with open(f'{temp_dir}/{mtl_path}', 'wb') as f:
            f.write(ZipFile(self.file).read(mtl_path))
        try:
            scene = pywavefront.Wavefront(f'{temp_dir}/{obj_path}')
        except Exception as e:
            raise ValidationError(_(f'Wavefront validation failed. {e}'))
        # remove directory and the content
        shutil.rmtree(temp_dir)
        return True
