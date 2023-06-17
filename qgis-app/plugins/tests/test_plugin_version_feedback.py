from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from plugins.models import Plugin, PluginVersion
from plugins.views import version_feedback_notify


class SetupMixin:
    fixtures = ["fixtures/auth.json"]

    @classmethod
    def setUpTestData(cls) -> None:
        cls.creator = User.objects.get(id=2)
        cls.staff = User.objects.get(id=3)
        cls.plugin = Plugin.objects.create(
            created_by=cls.creator,
            repository="http://example.com",
            tracker="http://example.com",
            package_name="test-feedback",
            name="test feedback",
            about="this is a test for plugin feedbacks"
        )
        cls.version = PluginVersion.objects.create(
            plugin=cls.plugin,
            created_by=cls.creator,
            min_qg_version="0.0.0",
            max_qg_version="99.99.99",
            version="0.1",
            approved=False,
            external_deps="test"
        )


class TestFeedbackNotify(SetupMixin, TestCase):
    def setUp(self) -> None:
        self.plugin.refresh_from_db()
        self.version.refresh_from_db()

    def test_version_feedback_notify_no_email(self):
        self.assertFalse(self.creator.email)
        with self.assertLogs(level='WARNING'):
            version_feedback_notify(self.version, self.creator)

    def test_version_feedback_notify_sent(self):
        self.creator.email = 'email@example.com'
        self.creator.save()
        with self.assertLogs(level='DEBUG'):
            version_feedback_notify(self.version, self.staff)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            f"Plugin {self.plugin} feedback notification."
        )
        self.assertIn(
            (
                "Plugin test feedback reviewed by staff and received a "
                "feedback.\nLink: "
                "http://example.com/plugins/test-feedback/version/0.1/feedback/"
                "\n"
            ),
            mail.outbox[0].body
        )
        self.assertEqual(
            mail.outbox[0].recipients(),
            ['email@example.com']
        )

    def test_add_recipient_in_email_notification(self):
        self.creator.email = 'email@example.com'
        self.creator.save()
        new_recipient = User.objects.create(
            username="new-recipient",
            email="new@example.com"
        )
        self.plugin.owners.add(new_recipient)
        self.assertListEqual(
            list(self.plugin.editors),
            [new_recipient, self.creator]
        )
        with self.assertLogs(level='DEBUG'):
            version_feedback_notify(self.version, self.staff)
        self.assertEqual(
            mail.outbox[0].recipients(),
            ['new@example.com', 'email@example.com']
        )
