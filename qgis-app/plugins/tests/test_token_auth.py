import os
from unittest.mock import patch

from django.urls import reverse
from django.test import Client, TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from plugins.models import Plugin, PluginVersion
from plugins.forms import PackageUploadForm
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

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

        package_name = self.plugin.package_name
        version = '0.0.1'
        self.url_add_version = reverse('version_create_api', args=[package_name])
        self.url_update_version = reverse('version_update_api', args=[package_name, version])
        self.url_token_list = reverse('plugin_token_list', args=[package_name])
        self.url_token_create = reverse('plugin_token_create', args=[package_name])

    def test_token_create(self):
        # Test token create
        response = self.client.post(self.url_token_create, {})
        self.assertEqual(response.status_code, 302)
        tokens = OutstandingToken.objects.all()
        self.assertEqual(tokens.count(), 1)

    def test_upload_new_version_with_valid_token(self):
        # Generate a token for the authenticated user
        self.client.post(self.url_token_create, {})
        outstanding_token = OutstandingToken.objects.last().token
        refresh = RefreshToken(outstanding_token)
        refresh['plugin_id'] = self.plugin.pk
        refresh['refresh_jti'] = refresh['jti']
        access_token = str(refresh.access_token)

        # Log out the user and use the token
        self.client.logout()

        valid_plugin = os.path.join(TESTFILE_DIR, "valid_plugin_0.0.2.zip_")
        with open(valid_plugin, "rb") as file:
            uploaded_file = SimpleUploadedFile(
                "valid_plugin_0.0.2.zip_", file.read(),
                content_type="application/zip_")

        c = Client(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Test POST request with access token
        response = c.post(self.url_add_version, {
            'package': uploaded_file,
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PluginVersion.objects.filter(plugin__name='Test Plugin', version='0.0.2').exists())

    def test_upload_new_version_with_invalid_token(self):
        # Log out the user and use the token
        self.client.logout()

        access_token = 'invalid_token'
        valid_plugin = os.path.join(TESTFILE_DIR, "valid_plugin_0.0.2.zip_")
        with open(valid_plugin, "rb") as file:
            uploaded_file = SimpleUploadedFile(
                "valid_plugin_0.0.2.zip_", file.read(),
                content_type="application/zip_")

        c = Client(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Test POST request with access token
        response = c.post(self.url_add_version, {
            'package': uploaded_file,
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(PluginVersion.objects.filter(plugin__name='Test Plugin', version='0.0.2').exists())

    def test_update_version_with_valid_token(self):
        # Generate a token for the authenticated user
        self.client.post(self.url_token_create, {})
        outstanding_token = OutstandingToken.objects.last().token
        refresh = RefreshToken(outstanding_token)
        refresh['plugin_id'] = self.plugin.pk
        refresh['refresh_jti'] = refresh['jti']
        access_token = str(refresh.access_token)

        # Log out the user and use the token
        self.client.logout()

        valid_plugin = os.path.join(TESTFILE_DIR, "valid_plugin_0.0.2.zip_")
        with open(valid_plugin, "rb") as file:
            uploaded_file = SimpleUploadedFile(
                "valid_plugin_0.0.2.zip_", file.read(),
                content_type="application/zip_")

        c = Client(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Test POST request with access token
        response = c.post(self.url_update_version, {
            'package': uploaded_file,
        })
        self.assertEqual(response.status_code, 302)
        # This will create a new version because this one is using token and doesn't have a created_by column
        self.assertTrue(PluginVersion.objects.filter(plugin__name='Test Plugin', version='0.0.1').exists())
        self.assertTrue(PluginVersion.objects.filter(plugin__name='Test Plugin', version='0.0.2').exists())

    def test_update_version_with_invalid_token(self):
        # Log out the user and use the token
        self.client.logout()
        access_token = 'invalid_token'

        valid_plugin = os.path.join(TESTFILE_DIR, "valid_plugin_0.0.2.zip_")
        with open(valid_plugin, "rb") as file:
            uploaded_file = SimpleUploadedFile(
                "valid_plugin_0.0.2.zip_", file.read(),
                content_type="application/zip_")

        c = Client(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # Test POST request with access token
        response = c.post(self.url_update_version, {
            'package': uploaded_file,
        })
        self.assertEqual(response.status_code, 403)
        self.assertTrue(PluginVersion.objects.filter(plugin__name='Test Plugin', version='0.0.1').exists())
        self.assertFalse(PluginVersion.objects.filter(plugin__name='Test Plugin', version='0.0.2').exists())