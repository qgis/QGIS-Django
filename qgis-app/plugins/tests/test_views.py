import os
import tempfile

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from plugins.models import PluginInvalid
from plugins.tests.model_factories import (UserF,
                                           PluginF,
                                           PluginVersionF,
                                           PluginInvalidF)


TESTFILE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'testfiles'))


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestInvalidPluginView(TestCase):
    """Test InvalidPlugin View"""

    # simplemenu will be loaded on base template. We need create its model
    fixtures = ['fixtures/simplemenu.json']

    def setUp(self) -> None:
        self.user = UserF.create()
        self.user.set_password('password')
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()

        valid_plugins = os.path.join(
            TESTFILE_DIR, "valid_metadata_link.zip")
        invalid_plugins = os.path.join(
            TESTFILE_DIR, "invalid_metadata_link.zip")
        self.valid_metadata_link = open(valid_plugins, 'rb')
        self.invalid_metadata_link = open(invalid_plugins, 'rb')

        self.plugin = PluginF.create(
            package_name="test_plugin"
        )

        # Create invalid plugins
        PluginInvalid.objects.all().delete()
        self.plugin_version_1 = PluginVersionF.create(
            version='0.0.0.0'
        )
        self.plugin_version_1.plugin.package_name = "test_modul"
        self.plugin_version_1.plugin.save()
        self.invalid_plugin_1 = PluginInvalidF.build(
            plugin=self.plugin_version_1.plugin)
        self.invalid_plugin_1.save()
        self.plugin_version_2 = PluginVersionF.create()
        self.invalid_plugin_2 = PluginInvalidF.build(
            plugin=self.plugin_version_2.plugin)
        self.invalid_plugin_2.save()

    def tearDown(self):
        self.valid_metadata_link.close()
        self.invalid_metadata_link.close()

    def test_PluginInvalid_list_should_return_invalid_plugin(self):
        self.assertEqual(PluginInvalid.objects.count(), 2)
        response = self.client.get(reverse('invalid_plugins'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.invalid_plugin_1.plugin.name)
        self.assertContains(response, self.invalid_plugin_2.plugin.name)
        self.assertNotContains(response, self.plugin.name)

    def test_update_plugin_should_remove_from_invalid_list(self):
        self.assertEqual(PluginInvalid.objects.count(), 2)
        url = reverse(
            'version_update',
            kwargs={
                "package_name": self.invalid_plugin_1.plugin.package_name,
                "version": self.invalid_plugin_1.validated_version
            })
        data = {
            "package": InMemoryUploadedFile(
                self.valid_metadata_link,
                field_name='tempfile',
                name='testfile.zip',
                content_type='application/zip',
                size=39889,
                charset='utf8'
            )
        }
        self.client.login(username=self.user.username, password="password")
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        # The updated plugin should be removed from the invalid list
        self.assertEqual(PluginInvalid.objects.count(), 1)

    def test_update_plugin_should_remove_from_invalid_list(self):
        self.assertEqual(PluginInvalid.objects.count(), 2)
        url = reverse(
            'version_update',
            kwargs={
                "package_name": self.invalid_plugin_1.plugin.package_name,
                "version": self.invalid_plugin_1.validated_version
            })
        data = {
            "package": InMemoryUploadedFile(
                self.valid_metadata_link,
                field_name='tempfile',
                name='testfile.zip',
                content_type='application/zip',
                size=39889,
                charset='utf8'
            )
        }
        self.client.login(username=self.user.username, password="password")
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        # The updated plugin should be removed from the invalid list
        self.assertEqual(PluginInvalid.objects.count(), 1)
        self.assertFalse(
            PluginInvalid.objects.filter(
                plugin__package_name=self.invalid_plugin_1.plugin.package_name
            ).exists()
        )

    def test_create_new_version_should_remove_plugin_from_invalid_list(self):
        self.assertEqual(PluginInvalid.objects.count(), 2)
        url = reverse(
            'version_create',
            kwargs={
                "package_name": "test_modul"
            })
        data = {
            "package": InMemoryUploadedFile(
                self.valid_metadata_link,
                field_name='tempfile',
                name='testfile.zip',
                content_type='application/zip',
                size=39889,
                charset='utf8'
            )
        }
        self.client.login(username=self.user.username, password="password")
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        # The updated plugin should be removed from the invalid list
        self.assertEqual(PluginInvalid.objects.count(), 1)
        self.assertFalse(
            PluginInvalid.objects.filter(
                plugin__package_name="test_modul"
            ).exists()
        )

