import datetime

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

from freezegun import freeze_time

from plugins.models import Plugin, PluginVersion, PluginVersionFeedback
from plugins.views import version_feedback_notify, version_feedback_resolved_notify
from django.conf import settings
from django.utils.dateformat import format
import json

class SetupMixin:
    fixtures = ["fixtures/auth.json", "fixtures/simplemenu.json"]

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

        # Should use the new email
        self.assertEqual(
            mail.outbox[0].from_email,
            settings.EMAIL_HOST_USER
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

        # Should use the new email
        self.assertEqual(
            mail.outbox[0].from_email,
            settings.EMAIL_HOST_USER
        )

class TestPluginFeedbackCompletedList(SetupMixin, TestCase):
    fixtures = ["fixtures/simplemenu.json", "fixtures/auth.json"]

    def setUp(self):
        super().setUp()
        self.feedback_1.is_completed = True
        self.feedback_1.save()
        self.url = reverse("feedback_completed_plugins")

    def test_non_staff_should_not_see_plugin_feedback_completed_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

        self.client.force_login(user=self.creator)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)
    
    def test_version_feedback_resolved_notify(self):

        with self.assertLogs(level='DEBUG'):
            version_feedback_resolved_notify(self.version_1, self.staff)
        self.assertEqual(
            mail.outbox[0].recipients(),
            ['admin@admin.it', 'staff@staff.it']
        )

        # Should use the new email
        self.assertEqual(
            mail.outbox[0].from_email,
            settings.EMAIL_HOST_USER
        )


    def test_staff_should_see_plugin_feedback_completed(self):
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

        # The plugin should not appear in the feedback completed list
        self.assertEqual(
            list(response.context['object_list']),
            [self.plugin_1]
        )
        self.assertNotContains(response, "test plugin 2")

    def test_approved_plugin_should_not_show_in_feedback_completed_list(self):
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
        object_list = set(response.context['object_list'])
        expected_objects = {self.plugin_1, self.plugin_2}
        self.assertEqual(object_list, expected_objects)
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


class TestCreateVersionFeedback(SetupMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse(
            "version_feedback",
            kwargs={
                "package_name": self.plugin_2.package_name,
                "version": self.version_2.version
            }
        )
        self.new_user = User.objects.create(
            username="new-user",
            is_staff=False
        )

    def test_version_feedback_required_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"/accounts/login/?next={self.url}"
        )

    def test_only_plugin_editor_and_staff_can_see_version_feedback_page(self):
        self.client.force_login(self.new_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
        self.client.force_login(user=self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_only_staff_can_see_new_feedback_form(self):
        self.client.force_login(user=self.creator)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<div class="new-feedback">')
        self.client.force_login(user=self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<div class="new-feedback">')

    def test_post_create_single_task_feedback(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            self.url,
            data={
                "feedback": "single line feedback"
            }
        )
        self.assertEqual(response.status_code, 302)
        feedbacks = PluginVersionFeedback.objects.filter(
            version=self.version_2).all()
        self.assertEqual(len(feedbacks), 1)
        self.assertEqual(feedbacks[0].task, "single line feedback")

    def test_post_create_multiple_task_feedback(self):
        self.client.force_login(self.staff)
        response = self.client.post(
            self.url,
            data={
                "feedback": "- [ ] task one\n - [ ] task two"
            }
        )
        self.assertEqual(response.status_code, 302)
        feedbacks = PluginVersionFeedback.objects.filter(
            version=self.version_2).all()
        self.assertEqual(len(feedbacks), 2)
        self.assertEqual(feedbacks[0].task, "task one")
        self.assertEqual(feedbacks[1].task, "task two")

    def test_post_create_invalid_bullet_point_1(self):
        self.client.force_login(self.staff)
        self.client.post(
            self.url,
            data={
                "feedback": "-[ ] invalid bullet point \n -[ ] invalid two"
            }
        )
        feedbacks = PluginVersionFeedback.objects.filter(
            version=self.version_2).all()
        self.assertEqual(len(feedbacks), 1)
        self.assertEqual(
            feedbacks[0].task,
            "-[ ] invalid bullet point \n -[ ] invalid two"
        )

    def test_post_create_invalid_bullet_point_2(self):
        self.client.force_login(self.staff)
        self.client.post(
            self.url,
            data={
                "feedback": ("-[ ] invalid bullet point\n"
                             " - [ ] only save valid bullet point")
            }
        )
        feedbacks = PluginVersionFeedback.objects.filter(
            version=self.version_2).all()
        self.assertEqual(len(feedbacks), 1)
        self.assertEqual(feedbacks[0].task, "only save valid bullet point")


class TestDeleteVersionFeedback(SetupMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse(
            "version_feedback_delete",
            kwargs={
                "package_name": self.plugin_1.package_name,
                "version": self.version_1.version,
                "feedback": self.feedback_1.id
            }
        )

    def test_only_the_reviewer_can_delete_a_feedback(self):
        self.client.force_login(user=self.creator)
        response = self.client.post(
            self.url,
            data={
                "status_feedback": "deleted"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.version_1.feedback.exists())
        self.client.force_login(user=self.staff)
        response = self.client.post(
            self.url,
            data={
                "status_feedback": "deleted"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.version_1.feedback.exists())


class TestUpdateVersionFeedback(SetupMixin, TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = reverse(
            "version_feedback_update",
            kwargs={
                "package_name": self.plugin_1.package_name,
                "version": self.version_1.version
            }
        )

    @freeze_time("2023-06-30 10:00:00")
    def test_staff_and_editor_can_update_feedback(self):
        feedbacks = self.version_1.feedback.all()
        self.assertEqual(len(feedbacks), 1)
        self.assertFalse(feedbacks[0].is_completed)
        self.client.force_login(user=self.creator)
        response = self.client.post(
            self.url,
            data={
                "completed_tasks": [feedbacks[0].id]
            }
        )
        self.assertEqual(response.status_code, 201)
        feedbacks = self.version_1.feedback.all()
        self.assertEqual(len(feedbacks), 1)
        self.assertTrue(feedbacks[0].is_completed)
        self.assertEqual(
            feedbacks[0].completed_on, datetime.datetime(2023, 6, 30, 10, 0, 0))

    def test_non_staff_and_non_editor_cannot_update_feedback(self):
        feedback = self.version_1.feedback.first()
        new_user = User.objects.create(username="new-user")
        self.client.force_login(user=new_user)
        self.client.post(
            self.url,
            data={
                "status_feedback": [feedback.id]
            }
        )
        feedback = self.version_1.feedback.first()
        self.assertFalse(feedback.is_completed)
        self.assertIsNone(feedback.completed_on)

class VersionFeedbackEditViewTests(SetupMixin, TestCase):

    def setUp(self):
        super().setUp()

    def test_version_feedback_edit_not_logged_in(self):
        url = reverse('version_feedback_edit', args=[self.plugin_1.package_name, self.version_1.version, self.feedback_1.pk])
        response = self.client.post(url, {'task': 'updated task'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_version_feedback_edit_logged_in_no_permission(self):
        self.user2 = User.objects.create_user(username='otheruser', password='password')
        self.client.login(username='otheruser', password='password')
        url = reverse('version_feedback_edit', args=[self.plugin_1.package_name, self.version_1.version, self.feedback_1.pk])
        response = self.client.post(url, {'task': 'updated task'})
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, {'success': False})

    def test_version_feedback_edit_logged_in_with_permission(self):
        self.client.force_login(user=self.creator)
        url = reverse('version_feedback_edit', args=[self.plugin_1.package_name, self.version_1.version, self.feedback_1.pk])
        response = self.client.post(url, {'task': 'updated task'})
        self.assertEqual(response.status_code, 201)
        self.feedback_1.refresh_from_db()
        self.assertEqual(self.feedback_1.task, 'updated task')
        self.assertIn('modified_on', response.json())

        response_modified_on = response.json()['modified_on']
        expected_modified_on = self.feedback_1.modified_on.isoformat()
        self.assertEqual(str(response_modified_on)[:20], expected_modified_on[:20])


    def test_version_feedback_edit_invalid_feedback(self):
        self.client.force_login(user=self.creator)
        invalid_feedback_id = self.feedback_1.pk + 1
        url = reverse('version_feedback_edit', args=[self.plugin_1.package_name, self.version_1.version, invalid_feedback_id])
        response = self.client.post(url, {'task': 'updated task'})
        self.assertEqual(response.status_code, 404)