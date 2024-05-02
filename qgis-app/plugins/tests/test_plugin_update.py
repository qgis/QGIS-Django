import os
from unittest.mock import patch

from django.urls import reverse
from django.test import Client, TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from plugins.models import Plugin, PluginVersion
from plugins.forms import PluginVersionForm
from django.core import mail
from django.conf import settings

def do_nothing(*args, **kwargs):
    pass

TESTFILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "testfiles"))

class PluginUpdateTestCase(TestCase):
    fixtures = [
        "fixtures/styles.json",
        "fixtures/auth.json",
        "fixtures/simplemenu.json",
    ]

    @override_settings(MEDIA_ROOT="api/tests")
    def setUp(self):
        self.client = Client()
        self.url_upload = reverse('plugin_upload')

        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )

        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Upload a plugin for renaming test. 
        # This process is already tested in test_plugin_upload
        valid_plugin = os.path.join(TESTFILE_DIR, "valid_plugin.zip_")
        with open(valid_plugin, "rb") as file:
            uploaded_file = SimpleUploadedFile(
                "valid_plugin.zip_", file.read(),
                content_type="application/zip")

        self.client.post(self.url_upload, {
            'package': uploaded_file,
        })

        self.plugin = Plugin.objects.get(name='Test Plugin')

    @patch("plugins.tasks.generate_plugins_xml", new=do_nothing)
    @patch("plugins.validator._check_url_link", new=do_nothing)
    def test_plugin_new_version(self):
        """
        Test upload a new plugin version with a modified metadata
        """
        package_name = self.plugin.package_name
        self.assertEqual(self.plugin.homepage, "https://example.net/")
        self.assertEqual(self.plugin.tracker, "https://example.net/")
        self.assertEqual(self.plugin.repository, "https://example.net/")
        self.url_add_version = reverse('version_create', args=[package_name])

        # Test POST request without allowing name from metadata
        valid_plugin = os.path.join(TESTFILE_DIR, "change_metadata.zip_")
        with open(valid_plugin, "rb") as file:
            uploaded_file = SimpleUploadedFile(
                "change_metadata.zip_", file.read(),
                content_type="application/zip_")

        response = self.client.post(self.url_add_version, {
            'package': uploaded_file,
            'experimental': False,
            'changelog': ''
        })
        self.assertEqual(response.status_code, 302)

        # The old version should always exist when creating a new version
        self.assertTrue(PluginVersion.objects.filter(
            plugin__name='Test Plugin', 
            version='0.0.1').exists()
        )
        self.assertTrue(PluginVersion.objects.filter(
            plugin__name='Test Plugin', 
            version='0.0.2').exists()
        )

        self.plugin = Plugin.objects.get(name='Test Plugin')
        self.assertEqual(self.plugin.homepage, "https://github.com/")
        self.assertEqual(self.plugin.tracker, "https://github.com/")
        self.assertEqual(self.plugin.repository, "https://github.com/")

        self.assertEqual(
            mail.outbox[0].recipients(),
            ['admin@admin.it', 'staff@staff.it']
        )

        # Should use the new email
        self.assertEqual(
            mail.outbox[0].from_email,
            settings.EMAIL_HOST_USER
        )

    @patch("plugins.tasks.generate_plugins_xml", new=do_nothing)
    @patch("plugins.validator._check_url_link", new=do_nothing)
    def test_plugin_version_update(self):
        """
        Test update a plugin version with a modified metadata
        """
        package_name = self.plugin.package_name
        self.assertEqual(self.plugin.homepage, "https://example.net/")
        self.assertEqual(self.plugin.tracker, "https://example.net/")
        self.assertEqual(self.plugin.repository, "https://example.net/")
        self.url_add_version = reverse('version_update', args=[package_name, '0.0.1'])

        # Test POST request without allowing name from metadata
        valid_plugin = os.path.join(TESTFILE_DIR, "change_metadata.zip_")
        with open(valid_plugin, "rb") as file:
            uploaded_file = SimpleUploadedFile(
                "change_metadata.zip_", file.read(),
                content_type="application/zip_")

        response = self.client.post(self.url_add_version, {
            'package': uploaded_file,
            'experimental': False,
            'changelog': ''
        })
        self.assertEqual(response.status_code, 302)

        # The old version should not exist anymore
        self.assertFalse(PluginVersion.objects.filter(
            plugin__name='Test Plugin', 
            version='0.0.1').exists()
        )
        self.assertTrue(PluginVersion.objects.filter(
            plugin__name='Test Plugin', 
            version='0.0.2').exists()
        )

        self.plugin = Plugin.objects.get(name='Test Plugin')
        self.assertEqual(self.plugin.homepage, "https://github.com/")
        self.assertEqual(self.plugin.tracker, "https://github.com/")
        self.assertEqual(self.plugin.repository, "https://github.com/")   

        self.assertEqual(
            mail.outbox[0].recipients(),
            ['admin@admin.it', 'staff@staff.it']
        )

        # Should use the new email
        self.assertEqual(
            mail.outbox[0].from_email,
            settings.EMAIL_HOST_USER
        )


    def tearDown(self):
        self.client.logout()
