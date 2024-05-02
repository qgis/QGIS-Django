import os
from unittest.mock import patch

from django.urls import reverse
from django.test import Client, TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from plugins.models import Plugin, PluginVersion
from plugins.forms import PluginVersionForm

def do_nothing(*args, **kwargs):
    pass

TESTFILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "testfiles"))

class PluginRenameTestCase(TestCase):
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
        self.plugin.name = "New name Test Plugin"
        self.plugin.save()

    @patch("plugins.tasks.generate_plugins_xml", new=do_nothing)
    @patch("plugins.validator._check_url_link", new=do_nothing)
    def test_plugin_rename(self):
        """
        Test rename from a new plugin version
        """
        package_name = self.plugin.package_name
        self.url_add_version = reverse('version_create', args=[package_name])
        # Test GET request
        response = self.client.get(self.url_add_version)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], PluginVersionForm)

        # Test POST request with invalid form data
        response = self.client.post(self.url_add_version, {})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

        # Test POST request without allowing name from metadata
        valid_plugin = os.path.join(TESTFILE_DIR, "valid_plugin_0.0.2.zip_")
        with open(valid_plugin, "rb") as file:
            uploaded_file = SimpleUploadedFile(
                "valid_plugin_0.0.2.zip_", file.read(),
                content_type="application/zip_")

        response = self.client.post(self.url_add_version, {
            'package': uploaded_file,
            'experimental': False,
            'changelog': ''
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PluginVersion.objects.filter(
            plugin__name='New name Test Plugin', 
            version='0.0.2').exists()
        )

        # Test POST request with allowing name from metadata
        self.plugin.allow_update_name = True
        self.plugin.save()

        valid_plugin = os.path.join(TESTFILE_DIR, "valid_plugin_0.0.3.zip_")
        with open(valid_plugin, "rb") as file:
            uploaded_file = SimpleUploadedFile(
                "valid_plugin_0.0.3.zip_", file.read(),
                content_type="application/zip_")
        response = self.client.post(self.url_add_version, {
            'package': uploaded_file,
            'experimental': False,
            'changelog': ''
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PluginVersion.objects.filter(
            plugin__name='Test Plugin', 
            version='0.0.3').exists()
        )

    def tearDown(self):
        self.client.logout()
