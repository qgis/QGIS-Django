from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from plugins.models import Plugin, PluginVersion, PluginVersionFeedback
from plugins.views import version_feedback_notify


class SetupMixin:
    fixtures = ["fixtures/auth.json"]

    def setUp(self) -> None:
        self.creator = User.objects.get(id=2)
        self.staff = User.objects.get(id=3)
        self.plugin_1 = Plugin.objects.create(
            created_by=self.creator,
            repository="http://example.com",
            tracker="http://example.com",
            package_name="test-feedback",
            name="test plugin 1",
            about="this is a test for plugin feedbacks",
            author="author plugin"
        )
        self.version_1 = PluginVersion.objects.create(
            plugin=self.plugin_1,
            created_by=self.creator,
            min_qg_version="0.0.0",
            max_qg_version="99.99.99",
            version="0.1",
            approved=False,
            external_deps="test"
        )
        self.feedback_1 = PluginVersionFeedback.objects.create(
            version=self.version_1,
            reviewer=self.staff,
            task="test comment in a feedback."
        )
        self.plugin_2 = Plugin.objects.create(
            created_by=self.creator,
            repository="http://example.com",
            tracker="http://example.com",
            package_name="plugin-test-2",
            name="test plugin 2",
            about="this is a test for plugin feedbacks",
            author="author plugin 2"
        )
        self.version_2 = PluginVersion.objects.create(
            plugin=self.plugin_2,
            created_by=self.creator,
            min_qg_version="0.0.0",
            max_qg_version="99.99.99",
            version="2.0",
            approved=False,
            external_deps="test"
        )


class TestFeedbackNotify(SetupMixin, TestCase):
    def test_version_feedback_notify_no_email(self):
        self.assertFalse(self.creator.email)
        with self.assertLogs(level='WARNING'):
            version_feedback_notify(self.version_1, self.creator)

    def test_version_feedback_notify_sent(self):
        self.creator.email = 'email@example.com'
        self.creator.save()
        with self.assertLogs(level='DEBUG'):
            version_feedback_notify(self.version_1, self.staff)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            f"Plugin {self.plugin_1} feedback notification."
        )
        self.assertIn(
            (
                "\nPlugin test plugin 1 reviewed by staff and received a "
                "feedback.\nLink: http://example.com/plugins/test-feedback/"
                "version/0.1/feedback/\n"
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
        self.plugin_1.owners.add(new_recipient)
        self.assertListEqual(
            list(self.plugin_1.editors),
            [new_recipient, self.creator]
        )
        with self.assertLogs(level='DEBUG'):
            version_feedback_notify(self.version_1, self.staff)
        self.assertEqual(
            mail.outbox[0].recipients(),
            ['new@example.com', 'email@example.com']
        )


class TestPluginFeedbackReceivedList(SetupMixin, TestCase):
    fixtures = ["fixtures/simplemenu.json", "fixtures/auth.json"]

    def setUp(self):
        super().setUp()
        self.url = reverse("feedback_received_plugins")

    def test_non_staff_should_not_see_plugin_feedback_received_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

        self.client.force_login(user=self.creator)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_staff_should_see_plugin_feedback_received(self):
        self.client.force_login(user=self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'plugins/plugin_list.html'
        )
        self.assertEqual(
            list(response.context['object_list']),
            [self.plugin_1]
        )
        self.assertContains(response, "test plugin 1")
        self.assertNotContains(response, "test plugin 2")

        # add feedback for plugin 2
        PluginVersionFeedback.objects.create(
            version=self.version_2,
            reviewer=self.staff,
            task="test comment in a feedback for plugin 2."
        )
        response = self.client.get(self.url)
        self.assertEqual(
            list(response.context['object_list']),
            [self.plugin_1, self.plugin_2]
        )
        self.assertContains(response, "test plugin 2")

    def test_approved_plugin_should_not_show_in_feedback_received_list(self):
        self.client.force_login(user=self.staff)
        response = self.client.get(self.url)
        self.assertEqual(
            list(response.context['object_list']),
            [self.plugin_1]
        )
        self.version_1.approved = True
        self.version_1.save()
        response = self.client.get(self.url)
        self.assertEqual(
            list(response.context['object_list']),
            []
        )


class TestPluginFeedbackPendingList(SetupMixin, TestCase):
    fixtures = ["fixtures/simplemenu.json", "fixtures/auth.json"]

    def setUp(self):
        super().setUp()
        self.url = reverse("feedback_pending_plugins")

    def test_non_staff_should_not_see_plugin_feedback_pending_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

        self.client.force_login(user=self.creator)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_staff_should_see_plugin_feedback_pending_list(self):
        self.client.force_login(user=self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'plugins/plugin_list.html'
        )
        self.assertEqual(
            list(response.context['object_list']),
            [self.plugin_2]
        )
        self.assertContains(response, "test plugin 2")
        self.assertNotContains(response, "test plugin 1")

        # add feedback for plugin 2
        PluginVersionFeedback.objects.create(
            version=self.version_2,
            reviewer=self.staff,
            task="test comment in a feedback for plugin 2."
        )
        response = self.client.get(self.url)
        self.assertEqual(
            list(response.context['object_list']),
            []
        )
