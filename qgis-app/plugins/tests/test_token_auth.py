import os
from unittest.mock import patch

from django.urls import reverse
from django.test import Client, TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from plugins.models import Plugin, PluginVersion
from plugins.forms import PackageUploadForm

def do_nothing(*args, **kwargs):
    pass

TESTFILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "testfiles"))

class UploadWithTokenTestCase(TestCase):
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

    def test_upload_with_token(self):
        create_token_url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }

        # Test POST request to create token
        response = self.client.post(create_token_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('access' in response.json())
        self.assertTrue('refresh' in response.json())

        access_token = response.json()['access']

        valid_plugin = os.path.join(TESTFILE_DIR, "valid_plugin.zip_")
        with open(valid_plugin, "rb") as file:
            uploaded_file = SimpleUploadedFile(
                "valid_plugin.zip_", file.read(),
                content_type="application/zip")

        c = Client(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        # Test POST request with access token
        response = c.post(self.url, {
            'package': uploaded_file,
        })


        self.assertEqual(response.status_code, 302)
        self.assertTrue(Plugin.objects.filter(name='Test Plugin').exists())
        self.assertEqual(
            Plugin.objects.get(name='Test Plugin').tags.filter(
                name__in=['python', 'example', 'test']).count(),
            3)
        self.assertTrue(PluginVersion.objects.filter(plugin__name='Test Plugin', version='0.0.1').exists())

    def test_refresh_token(self):
        create_token_url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }

        # Test POST request to create token
        response = self.client.post(create_token_url, data)
        refresh_token = response.json()['refresh']

        refresh_token_url = reverse('token_refresh')

        # Test POST request to create token
        refresh_data = {
            'refresh': refresh_token
        }
        response = self.client.post(refresh_token_url, refresh_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('access' in response.json())

        access_token = response.json()['access']

        valid_plugin = os.path.join(TESTFILE_DIR, "valid_plugin.zip_")
        with open(valid_plugin, "rb") as file:
            uploaded_file = SimpleUploadedFile(
                "valid_plugin.zip_", file.read(),
                content_type="application/zip")

        c = Client(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        # Test POST request with access token
        response = c.post(self.url, {
            'package': uploaded_file,
        })


        self.assertEqual(response.status_code, 302)
        self.assertTrue(Plugin.objects.filter(name='Test Plugin').exists())
        self.assertEqual(
            Plugin.objects.get(name='Test Plugin').tags.filter(
                name__in=['python', 'example', 'test']).count(),
            3)
        self.assertTrue(PluginVersion.objects.filter(plugin__name='Test Plugin', version='0.0.1').exists())



