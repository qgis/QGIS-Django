import os
import requests

from unittest import mock

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase


from plugins.validator import validator, _check_url_link

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

    @mock.patch('requests.get', side_effect=requests.exceptions.SSLError())
    def test_check_url_link_ssl_error(self, mock_request):
        url = 'http://example.com/'
        self.assertIsNone(
            _check_url_link(url, 'forbidden_url', 'metadata attribute')
        )

    @mock.patch('requests.get', side_effect=requests.exceptions.HTTPError())
    def test_check_url_link_does_not_exist(self, mock_request):
        url = 'http://example.com/'
        self.assertRaises(
            ValidationError,
            _check_url_link(url, 'forbidden_url', 'metadata attribute'),
        )


class TestValidatorForbiddenFileFolder(TestCase):
    """Test if zipfile is not containing forbidden folders and files """

    def setUp(self) -> None:
        valid_plugins = os.path.join(
            TESTFILE_DIR, "valid_metadata_link.zip")
        self.valid_metadata_link = open(valid_plugins, 'rb')
        self.package = InMemoryUploadedFile(
            self.valid_metadata_link,
            field_name='tempfile',
            name='testfile.zip',
            content_type='application/zip',
            size=1234,
            charset='utf8'
        )

    def tearDown(self):
        self.valid_metadata_link.close()

    @mock.patch('zipfile.ZipFile.namelist')
    def test_zipfile_with_pyc_file(self, mock_namelist):
        mock_namelist.return_value = ['.pyc']
        with self.assertRaisesMessage(
                Exception,
                'For security reasons, zip file cannot contain .pyc file'):
            validator(self.package)

    @mock.patch('zipfile.ZipFile.namelist')
    def test_zipfile_with_MACOSX(self, mock_namelist):
        mock_namelist.return_value = ['__MACOSX/']
        with self.assertRaisesMessage(
                Exception,
                ("For security reasons, zip file cannot contain "
                 "'__MACOSX' directory")):
            validator(self.package)

    @mock.patch('zipfile.ZipFile.namelist')
    def test_zipfile_with_pycache(self, mock_namelist):
        mock_namelist.return_value = ['__pycache__/']
        with self.assertRaisesMessage(
                Exception,
                ("For security reasons, zip file cannot contain "
                 "'__pycache__' directory")):
            validator(self.package)

    @mock.patch('zipfile.ZipFile.namelist')
    def test_zipfile_with_git(self, mock_namelist):
        mock_namelist.return_value = ['.git']
        with self.assertRaisesMessage(
                Exception,
                ("For security reasons, zip file cannot contain "
                 "'.git' directory")):
            validator(self.package)

    @mock.patch('zipfile.ZipFile.namelist')
    def test_zipfile_with_gitignore(self, mock_namelist):
        """test if .gitignore will not raise ValidationError"""
        mock_namelist.return_value = ['.gitignore']
        with self.assertRaises(ValidationError) as cm:
            validator(self.package)
        exception = cm.exception
        self.assertNotEqual(
            exception.message,
            "For security reasons, zip file cannot contain '.git' directory")
