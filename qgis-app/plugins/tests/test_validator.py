import os
from unittest import mock

import requests
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase
from plugins.validator import _check_url_link, validator

TESTFILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "testfiles"))


class TestValidatorMetadataPlugins(TestCase):
    def setUp(self):
        invalid_plugins = os.path.join(TESTFILE_DIR, "invalid_metadata_link.zip")
        invalid_url_scheme_plugins = os.path.join(
            TESTFILE_DIR, "invalid_url_scheme.zip"
        )
        web_not_exist_plugins = os.path.join(TESTFILE_DIR, "web_not_exist.zip")
        valid_plugins = os.path.join(TESTFILE_DIR, "valid_metadata_link.zip")
        self.valid_metadata_link = open(valid_plugins, "rb")
        self.invalid_metadata_link = open(invalid_plugins, "rb")
        self.web_not_exist = open(web_not_exist_plugins, "rb")
        self.invalid_url_scheme = open(invalid_url_scheme_plugins, "rb")

    def tearDown(self):
        self.valid_metadata_link.close()
        self.invalid_metadata_link.close()
        self.invalid_url_scheme.close()
        self.web_not_exist.close()

    def test_valid_metadata(self):
        self.assertTrue(
            validator(
                InMemoryUploadedFile(
                    self.valid_metadata_link,
                    field_name="tempfile",
                    name="testfile.zip",
                    content_type="application/zip",
                    size=39889,
                    charset="utf8",
                )
            )
        )

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
                field_name="tempfile",
                name="testfile.zip",
                content_type="application/zip",
                size=39889,
                charset="utf8",
            ),
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
                field_name="tempfile",
                name="testfile.zip",
                content_type="application/zip",
                size=39889,
                charset="utf8",
            ),
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
                field_name="tempfile",
                name="testfile.zip",
                content_type="application/zip",
                size=39889,
                charset="utf8",
            ),
        )

    @mock.patch("requests.get", side_effect=requests.exceptions.SSLError())
    def test_check_url_link_ssl_error(self, mock_request):
        urls = [{'url': "http://example.com/", 'forbidden_url': "forbidden_url", 'metadata_attr': "metadata attribute"}]
        self.assertIsNone(_check_url_link(urls))

    @mock.patch("requests.get", side_effect=requests.exceptions.HTTPError())
    def test_check_url_link_does_not_exist(self, mock_request):
        urls = [{'url': "http://example.com/", 'forbidden_url': "forbidden_url", 'metadata_attr': "metadata attribute"}]
        self.assertIsNone(_check_url_link(urls))


class TestValidatorForbiddenFileFolder(TestCase):
    """Test if zipfile is not containing forbidden folders and files """

    def setUp(self) -> None:
        valid_plugins = os.path.join(TESTFILE_DIR, "valid_metadata_link.zip")
        self.valid_metadata_link = open(valid_plugins, "rb")
        self.package = InMemoryUploadedFile(
            self.valid_metadata_link,
            field_name="tempfile",
            name="testfile.zip",
            content_type="application/zip",
            size=1234,
            charset="utf8",
        )

    def tearDown(self):
        self.valid_metadata_link.close()

    @mock.patch("zipfile.ZipFile.namelist")
    def test_zipfile_with_pyc_file(self, mock_namelist):
        mock_namelist.return_value = [".pyc"]
        with self.assertRaisesMessage(
            Exception, "For security reasons, zip file cannot contain .pyc file"
        ):
            validator(self.package)

    @mock.patch("zipfile.ZipFile.namelist")
    def test_zipfile_with_MACOSX(self, mock_namelist):
        mock_namelist.return_value = ["__MACOSX/"]
        with self.assertRaisesMessage(
            Exception,
            ("For security reasons, zip file cannot contain " "'__MACOSX' directory"),
        ):
            validator(self.package)

    @mock.patch("zipfile.ZipFile.namelist")
    def test_zipfile_with_pycache(self, mock_namelist):
        mock_namelist.return_value = ["__pycache__/"]
        with self.assertRaisesMessage(
            Exception,
            (
                "For security reasons, zip file cannot contain "
                "'__pycache__' directory"
            ),
        ):
            validator(self.package)

    @mock.patch("zipfile.ZipFile.namelist")
    def test_zipfile_with_git(self, mock_namelist):
        mock_namelist.return_value = [".git"]
        with self.assertRaisesMessage(
            Exception,
            ("For security reasons, zip file cannot contain " "'.git' directory"),
        ):
            validator(self.package)

    @mock.patch("zipfile.ZipFile.namelist")
    def test_zipfile_with_gitignore(self, mock_namelist):
        """test if .gitignore will not raise ValidationError"""
        mock_namelist.return_value = [".gitignore"]
        with self.assertRaises(ValidationError) as cm:
            validator(self.package)
        exception = cm.exception
        self.assertNotEqual(
            exception.message,
            "For security reasons, zip file cannot contain '.git' directory",
        )


class TestLicenseValidator(TestCase):
    """Test if zipfile contains LICENSE file """    

    def setUp(self) -> None:
        plugin_without_license = os.path.join(TESTFILE_DIR, "plugin_without_license.zip_")
        self.plugin_package = open(plugin_without_license, "rb")

    def tearDown(self):
        self.plugin_package.close()

    # License file is just recommended for now
    # def test_new_plugin_without_license(self):
    #     self.assertRaises(
    #         ValidationError,
    #         validator,
    #         InMemoryUploadedFile(
    #             self.plugin_package,
    #             field_name="tempfile",
    #             name="testfile.zip",
    #             content_type="application/zip",
    #             size=39889,
    #             charset="utf8",
    #         ),
    #         plugin_is_new=True
    #     )

    def test_plugin_without_license(self):
        self.assertTrue(
            validator(
                InMemoryUploadedFile(
                    self.plugin_package,
                    field_name="tempfile",
                    name="testfile.zip",
                    content_type="application/zip",
                    size=39889,
                    charset="utf8",
                )
            )
        )

class TestMultipleParentFoldersValidator(TestCase):
    """Test if zipfile contains multiple parent folders """    

    def setUp(self) -> None:
        multi_parents_plugin = os.path.join(TESTFILE_DIR, "multi_parents_plugin.zip_")
        self.multi_parents_plugin_package = open(multi_parents_plugin, "rb")
        valid_plugin = os.path.join(TESTFILE_DIR, "valid_plugin.zip_")
        self.single_parent_plugin_package = open(valid_plugin, "rb")

    def tearDown(self):
        self.multi_parents_plugin_package.close()
        self.single_parent_plugin_package.close()

    def _get_value_by_attribute(self, attribute, data):
        for key, value in data:
            if key == attribute:
                return value
        return None
    def test_plugin_with_multiple_parents(self):
        result =  validator(
            InMemoryUploadedFile(
                self.multi_parents_plugin_package,
                field_name="tempfile",
                name="testfile.zip",
                content_type="application/zip",
                size=39889,
                charset="utf8",
            )
        )
        multiple_parent_folders = self._get_value_by_attribute('multiple_parent_folders', result)
        self.assertIsNotNone(multiple_parent_folders)

    def test_plugin_with_single_parent(self):
        result =  validator(
            InMemoryUploadedFile(
                self.single_parent_plugin_package,
                field_name="tempfile",
                name="testfile.zip",
                content_type="application/zip",
                size=39889,
                charset="utf8",
            )
        )
        multiple_parent_folders = self._get_value_by_attribute('multiple_parent_folders', result)
        self.assertIsNone(multiple_parent_folders)
