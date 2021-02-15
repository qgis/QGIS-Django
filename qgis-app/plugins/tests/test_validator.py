import os

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase


from plugins.validator import validator

TESTFILE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'testfiles'))


class TestValidatorMetadataPlugins(TestCase):

    def setUp(self):
        invalid_plugins = os.path.join(
            TESTFILE_DIR, "invalid_metadata_link.zip")
        invalid_url_scheme_plugins = os.path.join(
            TESTFILE_DIR, "invalid_url_scheme.zip")
        web_not_exist_plugins= os.path.join(
            TESTFILE_DIR, "web_not_exist.zip")
        valid_plugins = os.path.join(
            TESTFILE_DIR, "valid_metadata_link.zip")
        self.valid_metadata_link = open(valid_plugins, 'rb')
        self.invalid_metadata_link = open(invalid_plugins, 'rb')
        self.web_not_exist = open(web_not_exist_plugins, 'rb')
        self.invalid_url_scheme = open(invalid_url_scheme_plugins,'rb')

    def tearDown(self):
        self.valid_metadata_link.close()
        self.invalid_metadata_link.close()
        self.invalid_url_scheme.close()
        self.web_not_exist.close()

    def test_valid_metadata(self):
        self.assertTrue(validator(
            InMemoryUploadedFile(
                self.valid_metadata_link,
                field_name='tempfile',
                name='testfile.zip',
                content_type='application/zip',
                size=39889,
                charset='utf8'
            )
        ))

    def test_invalid_metadata_link_tracker_repo_homepage(self):
        """
        The invalid_metadata_link.zip contains metadata file with default link
        value.

        bug tracker : http://bugs
        repo :  http://repo
        homepage : http://homepage
        """

        self.assertRaises(
            ValidationError,
            validator,
            InMemoryUploadedFile(
                self.invalid_metadata_link,
                field_name='tempfile',
                name='testfile.zip',
                content_type='application/zip',
                size=39889,
                charset='utf8'
            )
        )

    def test_invalid_metadata_url_scheme(self):
        """
        The invalid_url_scheme.zip contains metadata file with
        invalid scheme.

        bug tracker : https  ://www.example.com/invalid-url-scheme
        repo :  https://plugins.qgis.org/
        homepage: https://plugins.qgis.org/
        """

        self.assertRaises(
            ValidationError,
            validator,
            InMemoryUploadedFile(
                self.invalid_url_scheme,
                field_name='tempfile',
                name='testfile.zip',
                content_type='application/zip',
                size=39889,
                charset='utf8'
            )
        )

    def test_invalid_metadata_web_does_not_exist(self):
        """
        The invalid_url_scheme.zip contains metadata file with
        invalid scheme.

        bug tracker : http://www.example.com
        repo :  http://www.example.com/this-not-exist
        homepage: http://www.example.com
        """

        self.assertRaises(
            ValidationError,
            validator,
            InMemoryUploadedFile(
                self.web_not_exist,
                field_name='tempfile',
                name='testfile.zip',
                content_type='application/zip',
                size=39889,
                charset='utf8'
            )
        )

