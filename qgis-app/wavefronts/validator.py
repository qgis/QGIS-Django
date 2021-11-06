"""Wavefront validator."""

import os
import pywavefront
import re
import shutil
import uuid
from zipfile import ZipFile
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from wavefronts.models import WAVEFRONTS_STORAGE_PATH


class WavefrontValidator:

    def __init__(self, file):
        self.file = file

    def valid_zip(self):
        try:
            zip_file = ZipFile(self.file)
        except Exception:
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
                return True
        raise ValidationError(_('Could not find .mtl file.'))

    def extract_zipfile(self, target_dir):
        with ZipFile(self.file) as zip:
            for zip_info in zip.infolist():
                if zip_info.filename[-1] == '/':
                    continue
                zip_info.filename = os.path.basename(zip_info.filename)
                zip.extract(zip_info, target_dir)

    def validate_wavefront(self):
        self.is_mtl_file_exist()
        obj_path = self.get_wavefront_obj_path()
        filename, ext = os.path.splitext(obj_path)
        mtl_path = f'{filename}.mtl'

        unique_hex = uuid.uuid4().hex[0:6]
        temp_dir = f'/tmp/{unique_hex}'

        # create new directory for temporary file
        path, filename = os.path.split(obj_path)
        filename, ext = os.path.splitext(filename)
        obj_file = f'{filename}.obj'
        mtl_file = f'{filename}.mtl'
        dummy_file = f'{filename}.dummy'


        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        with open(f'{temp_dir}/{obj_file}', 'wb') as f_obj:
            f_obj.write(ZipFile(self.file).read(obj_path))
        with open(f'{temp_dir}/{mtl_file}', 'wb') as f_mtl:
            f_mtl.write(ZipFile(self.file).read(mtl_path))

        try:
            pywavefront.Wavefront(f'{temp_dir}/{obj_file}')
        except Exception as e:
            raise ValidationError(_(f'Wavefront validation failed. {e}'))

        # save to media directory
        media_dir = os.path.join(settings.MEDIA_ROOT, WAVEFRONTS_STORAGE_PATH)
        save_dir = f'{media_dir}/{unique_hex}'
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        self.extract_zipfile(save_dir)

        # remove temp directory and the content
        shutil.rmtree(temp_dir)

        return f'{unique_hex}/{dummy_file}'
