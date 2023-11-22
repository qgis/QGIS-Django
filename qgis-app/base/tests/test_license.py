import os
from zipfile import ZipFile

from base.license import zipped_with_license
from django.test import TestCase

TESTFILES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "testfiles"))


class TestZippedWithLicense(TestCase):
    def setUp(self):
        self.file = os.path.join(TESTFILES_DIR, "test.txt")

    def test_zipped_with_license(self):
        zipfile = zipped_with_license(self.file, "test")
        zf = ZipFile(zipfile).namelist()
        self.assertEqual(zf, ["test/test.txt", "test/license.txt"])
