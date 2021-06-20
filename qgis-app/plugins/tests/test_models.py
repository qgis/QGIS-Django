import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase, override_settings

from plugins.models import PluginVersion, Plugin, PluginInvalid

TESTFILE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'testfiles'))


@override_settings(MEDIA_ROOT='plugins/tests/testfiles/')
@override_settings(MEDIA_URL='plugins/tests/testfiles/')
class TestPluginInvalidModel(TestCase):

    def setUp(self) -> None:
        self.creator = User.objects.create(
            username='usertest_creator',
            first_name="first_name",
            last_name="last_name",
            email="creator@example.com",
            password="passwordtest",
            is_active=True)
        self.author = User.objects.create(
            username='usertest_author',
            first_name="author",
            last_name="last_name",
            email="author@example.com",
            password="passwordtest",
            is_active=True)

        invalid_plugin = os.path.join(
            TESTFILE_DIR, "web_not_exist.zip")
        self.invalid_plugin = open(invalid_plugin, 'rb')

        uploaded_zipfile = InMemoryUploadedFile(
            self.invalid_plugin,
            field_name='tempfile',
            name='testfile.zip',
            content_type='application/zip',
            size=39889,
            charset='utf8')

        self.plugin = Plugin.objects.create(
            created_by=self.creator,
            name='test_plugin',
            package_name='test_plugin'
        )

        self.version = PluginVersion.objects.create(
            plugin=self.plugin,
            created_by=self.creator,
            version='0.1',
            package=uploaded_zipfile,
            min_qg_version='3.10',
            max_qg_version='3.18'
        )

    def tearDown(self) -> None:
        self.invalid_plugin.close()
        os.remove(self.version.package.url)

    def test_create_PluginInvalid_instance(self):
        invalid_plugin = PluginInvalid.objects.create(
            plugin=self.plugin,
            validated_version=self.plugin.pluginversion_set.get().version
        )
        self.assertEqual(invalid_plugin.validated_version, '0.1')
        self.assertIsNotNone(invalid_plugin.validated_at)
