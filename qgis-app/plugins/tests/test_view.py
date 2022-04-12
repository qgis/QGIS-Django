from django.test import TestCase

from plugins.views import _add_patch_version


class TestTruncateVersion(TestCase):
    """Test _add_patch_version function"""

    def test__add_patch_version_with_3_segment_version_number(self):
        version = '1.2.3'
        self.assertEqual(_add_patch_version(version, '99'), '1.2.3')

    def test__add_patch_version_with_2_segment_version_number(self):
        version = '1.2'
        self.assertEqual(_add_patch_version(version, '00'), '1.2.00')

    def test__add_patch_version_with_1_segment_version_number(self):
        version = '1'
        self.assertEqual(_add_patch_version(version, '99'), '1')

    def test__add_patch_version_with_None(self):
        version = None
        self.assertEqual(_add_patch_version(version, '99'), None)

    def test__add_patch_version_with_empty_string(self):
        version = ''
        self.assertEqual(_add_patch_version(version, '99'), '')
