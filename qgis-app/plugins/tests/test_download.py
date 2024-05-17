from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from plugins.models import Plugin, PluginVersion, PluginVersionDownload
from plugins.views import version_download

from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from unittest.mock import patch
from plugins.forms import VersionDownloadForm

class TestVersionDownloadView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )

        self.plugin = Plugin.objects.create(
            package_name="test-package",
            created_by=self.user,
        )

        self.version = PluginVersion.objects.create(
            plugin=self.plugin,
            version="1.0.0",
            downloads=0,
            created_by=self.user,
            package=SimpleUploadedFile("test.zip", b"file_content"),
            min_qg_version='3.1.1',
            max_qg_version='3.3.0'
        )

    def test_version_download(self):
        request = self.factory.get('/')

        response = version_download(request, self.plugin.package_name, self.version.version)

        self.version.refresh_from_db()
        self.plugin.refresh_from_db()
        download_record = PluginVersionDownload.objects.get(
            plugin_version=self.version, 
            download_date=timezone.now().date()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/zip')
        self.assertEqual(response.content, b'file_content')

        self.assertEqual(self.version.downloads, 1)
        self.assertEqual(self.plugin.downloads, 1)
        self.assertEqual(download_record.download_count, 1)


class VersionGetViewTest(TestCase):
    fixtures = [
        "fixtures/styles.json",
        "fixtures/auth.json",
        "fixtures/simplemenu.json",
    ]
    def setUp(self):
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            username='testuser',
            password='12345'
        )

        self.plugin = Plugin.objects.create(
            package_name="test-package",
            created_by=self.user,
            name="Test Package"
        )

        self.version = PluginVersion.objects.create(
            plugin=self.plugin,
            version="1.0.0",
            downloads=0,
            created_by=self.user,
            package=SimpleUploadedFile("test.zip", b"file_content"),
            min_qg_version='3.1.1',
            max_qg_version='3.3.0'
        )
        self.url = reverse(
            'version_get', 
            kwargs={
                'package_name': self.plugin.package_name, 
                'version': self.version.version
            }
        )

        self.ip = '127.0.0.1'
        self.cache_key = f'download_limit_{self.ip}'
        settings.DOWNLOAD_RATE_LIMIT = 5  # Set a rate limit for testing

    def tearDown(self):
        # Clear cache after each test
        cache.clear()

    def test_rate_limit_not_exceeded(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plugins/plugin_download.html')

    def test_rate_limit_exceeded(self):
        # Simulate exceeding the rate limit
        cache.set(self.cache_key, settings.DOWNLOAD_RATE_LIMIT, timeout=60)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 429)
        self.assertTemplateUsed(response, 'plugins/plugin_download_limit_exceed.html')

    def test_successful_download_post(self):
        # Mocking _get_file_content function
        with patch('plugins.views._get_file_content') as mock_get_file_content:
            mock_get_file_content.return_value = ('file_content', 'file.zip')
            response = self.client.post(self.url, {'plugin_name': 'Test Package'})  # Adjust form data as needed
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'plugins/plugin_download_success.html')
            self.assertIn('file_content', response.context)
            self.assertIn('file_name', response.context)
            self.assertIn('plugin_name', response.context)

    def test_form_display_on_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plugins/plugin_download.html')
        self.assertIsInstance(response.context['form'], VersionDownloadForm)
        self.assertEqual(response.context['plugin_name'], self.plugin.name)