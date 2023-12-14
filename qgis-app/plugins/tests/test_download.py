from django.test import Client, TestCase, RequestFactory
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from plugins.models import Plugin, PluginVersion, PluginVersionDownload, PluginDownloadEvent
from plugins.views import version_download
from django.urls import reverse

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

    def test_version_download_per_country(self):
        download_url = reverse('version_download', args=[self.plugin.package_name, self.version.version])
        c = Client(REMOTE_ADDR='180.247.213.170')
        response = c.get(download_url)

        self.version.refresh_from_db()
        self.plugin.refresh_from_db()
        download_event = PluginDownloadEvent.objects.get(
            plugin_version=self.version
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(download_event.country_code == 'ID')