import os
from unittest.mock import patch

from django.urls import reverse
from django.test import Client, TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from plugins.models import Plugin, PluginVersion
from plugins.forms import PackageUploadForm
from django.core import mail
from django.conf import settings

def do_nothing(*args, **kwargs):
    pass

TESTFILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "testfiles"))

class PluginUploadTestCase(TestCase):
    fixtures = [
        "fixtures/styles.json",
        "fixtures/auth.json",
        "fixtures/simplemenu.json",
    ]

    @override_settings(MEDIA_ROOT="api/tests")
    def setUp(self):
        self.client = Client()
        self.url = reverse('plugin_upload')

        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )

    @patch("plugins.tasks.generate_plugins_xml.delay", new=do_nothing)
    @patch("plugins.validator._check_url_link", new=do_nothing)
    def test_plugin_upload_form(self):
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Test GET request
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], PackageUploadForm)

        # Test POST request with invalid form data
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())

        valid_plugin = os.path.join(TESTFILE_DIR, "valid_plugin.zip_")
        with open(valid_plugin, "rb") as file:
            uploaded_file = SimpleUploadedFile(
                "valid_plugin.zip_", file.read(),
                content_type="application/zip")

        # Test POST request with valid form data
        response = self.client.post(self.url, {
            'package': uploaded_file,
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Plugin.objects.filter(name='Test Plugin').exists())
        self.assertEqual(
            Plugin.objects.get(name='Test Plugin').tags.filter(
                name__in=['python', 'example', 'test']).count(),
            3)
        self.assertTrue(PluginVersion.objects.filter(plugin__name='Test Plugin', version='0.0.1').exists())

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
