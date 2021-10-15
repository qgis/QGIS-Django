import os
from unittest import mock
from django.core.exceptions import ValidationError
from django.test import TestCase
from wavefronts.validator import WavefrontValidator


WAVEFRONT_DIR = os.path.join(os.path.dirname(__file__), "wavefrontfiles")


class TestWavefrontValidator(TestCase):
    def setUp(self) -> None:
        self.mocked_obj = mock.Mock()
        self.mocked_obj.filename = 'root_dir/test.obj'
        self.mocked_mtl = mock.Mock()
        self.mocked_mtl.filename = 'root_dir/test.mtl'
        self.mocked_mtl_random = mock.Mock()
        self.mocked_mtl_random.filename = 'root_dir/random.mtl'

    def test_get_wavefront_obj_path_succeed(self):
        with mock.patch('wavefronts.validator.WavefrontValidator.valid_zip') \
                as mocked:
            valid_zip = mocked.return_value
            valid_zip.filelist = [self.mocked_obj, self.mocked_mtl]
            wv = WavefrontValidator('test.zip')
            self.assertEqual(
                wv.get_wavefront_obj_path(),
                'root_dir/test.obj'
            )

    def test_get_wavefront_obj_path_cannot_find_obj_file(self):
        with mock.patch('wavefronts.validator.WavefrontValidator.valid_zip') \
                as mocked:
            valid_zip = mocked.return_value
            valid_zip.filelist = [self.mocked_mtl]
            wv = WavefrontValidator('test.zip')
            with self.assertRaises(ValidationError) as error:
                wv.get_wavefront_obj_path()
            self.assertEqual(
                str(error.exception.message),
                'Could not find .obj file.'
            )

    def test_is_mtl_file_exist_succeed(self):
        with mock.patch('wavefronts.validator.WavefrontValidator.valid_zip') \
                as mocked:
            valid_zip = mocked.return_value
            valid_zip.filelist = [self.mocked_obj, self.mocked_mtl]
            wv = WavefrontValidator('test.zip')
            self.assertTrue(wv.is_mtl_file_exist())

    def test_is_mtl_file_exist_cannot_find_mtl(self):
        with mock.patch('wavefronts.validator.WavefrontValidator.valid_zip') \
                as mocked:
            valid_zip = mocked.return_value
            valid_zip.filelist = [self.mocked_obj, self.mocked_mtl_random]
            wv = WavefrontValidator('test.zip')
            with self.assertRaises(ValidationError) as error:
                wv.is_mtl_file_exist()
            self.assertEqual(
                str(error.exception.message),
                'Could not find .mtl file.'
            )

    def test_validate_wavefront(self):
        valid_wavefront = os.path.join(WAVEFRONT_DIR, "odm_texturing_25d.zip")
        wv = WavefrontValidator(valid_wavefront)
        self.assertTrue(wv.validate_wavefront())
