import os

from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.test import TestCase, override_settings

from plugins.models import PluginVersion, Plugin
from plugins.management.commands.validate_existing_plugins import (
    validate_zipfile_version, send_email_notification)

TESTFILE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'testfiles'))


@override_settings(MEDIA_ROOT='plugins/tests/testfiles/')
@override_settings(MEDIA_URL='plugins/tests/testfiles/')
class TestValidateExistingPlugin(TestCase):
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

    def test_plugin_exist(self):
        self.assertEqual(PluginVersion.objects.count(), 1)
        self.assertTrue(os.path.exists(self.version.package.url))

    def test_validate_zipfile_version(self):
        expected_value = {
            'plugin': 'test_plugin',
            'created_by': 'usertest_creator',
            'version': '0.1',
            'msg': ['Please provide valid url link for Repository in metadata. '
                    'This website cannot be reached.'],
            'url': 'http://plugins.qgis.org/plugins/test_plugin/version/0.1/',
            'recipients_email': ['creator@example.com']}
        self.assertEqual(
            validate_zipfile_version(self.version),
            expected_value,
            msg=validate_zipfile_version(self.version)
        )

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_send_email(self):
        error_msg = validate_zipfile_version(self.version)
        send_email_notification(
            plugin=error_msg['plugin'],
            version=error_msg['version'],
            message='\r\n'.join(error_msg['msg']),
            url_version=error_msg['url'],
            recipients=error_msg['recipients_email']
        )

    def test_send_email_must_contains(self):
        error_msg = validate_zipfile_version(self.version)
        send_email_notification(
            plugin=error_msg['plugin'],
            version=error_msg['version'],
            message='\r\n'.join(error_msg['msg']),
            url_version=error_msg['url'],
            recipients=error_msg['recipients_email']
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'Invalid Plugin Metadata Notification')
        self.assertIn(
            'Please update Plugin: test_plugin - Version: 0.1',
            mail.outbox[0].body)
        self.assertIn(
            'Please provide valid url link for Repository in metadata. '
            'This website cannot be reached.',
            mail.outbox[0].body)
