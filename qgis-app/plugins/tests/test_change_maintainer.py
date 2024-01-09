import os
from unittest.mock import patch

from django.urls import reverse
from django.test import Client, TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from plugins.models import Plugin, PluginVersion
from plugins.forms import PluginForm

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
        self.plugin.save()

    @patch("plugins.tasks.generate_plugins_xml.delay", new=do_nothing)
    @patch("plugins.validator._check_url_link", new=do_nothing)
    def test_change_maintainer(self):
        """
        Test change maintainer for plugin update
        """
        package_name = self.plugin.package_name
        self.url_plugin_update = reverse('plugin_update', args=[package_name])
        self.url_add_version = reverse('version_create', args=[package_name])

        # Test GET request
        response = self.client.get(self.url_plugin_update)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], PluginForm)
        self.assertEqual(response.context['form']['maintainer'].value(), self.user.pk)


        # Test POST request to change maintainer

        response = self.client.post(self.url_plugin_update, {
            'description': self.plugin.description,
            'about': self.plugin.about,
            'author': self.plugin.author,
            'email': self.plugin.email,
            'tracker': self.plugin.tracker,
            'repository': self.plugin.repository,
            'maintainer': 1,
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Plugin.objects.get(name='Test Plugin').maintainer.pk, 1)

        # Test POST request with new version

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
        self.assertEqual(Plugin.objects.get(name='Test Plugin').maintainer.pk, 1)

    def tearDown(self):
        self.client.logout()
