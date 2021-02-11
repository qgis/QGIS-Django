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
        partial_invalid_plugins = os.path.join(
            TESTFILE_DIR, "partial_invalid_metadata_link.zip")
        valid_plugins = os.path.join(
            TESTFILE_DIR, "valid_metadata_link.zip")
        self.valid_metadata_link = open(valid_plugins, 'rb')
        self.invalid_metadata_link = open(invalid_plugins, 'rb')
        self.partial_invalid_metadata_link = open(partial_invalid_plugins,
                                                  'rb')

    def tearDown(self):
        self.valid_metadata_link.close()
        self.invalid_metadata_link.close()
        self.partial_invalid_metadata_link.close()

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

    def test_partial_invalid_metadata_link_tracker_repo_homepage(self):
        """
        The partial_invalid_metadata_link.zip contains metadata file with
        some default link value.

        bug tracker : http://bugs
        repo :  http://repo
        homepage: http://homepage-valid.example.com
        """

        self.assertRaises(
            ValidationError,
            validator,
            InMemoryUploadedFile(
                self.partial_invalid_metadata_link,
                field_name='tempfile',
                name='testfile.zip',
                content_type='application/zip',
                size=39889,
                charset='utf8'
            )
        )

