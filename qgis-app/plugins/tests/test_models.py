from datetime import datetime

from freezegun import freeze_time

from django.contrib.auth.models import User
from django.test import TestCase
from plugins.models import Plugin, PluginVersion, PluginVersionFeedback


class PluginVersionFeedbackTest(TestCase):
    fixtures = ["fixtures/auth.json", ]

    def setUp(self):
        self.creator = User.objects.get(id=2)
        self.admin = User.objects.get(id=1)
        self.staff = User.objects.get(id=3)
        self.plugin = Plugin.objects.create(
            created_by=self.creator,
            repository="http://example.com",
            tracker="http://example.com",
            package_name="test-feedback",
            name="test feedback",
            about="this is a test for plugin feedbacks"
        )
        self.version = PluginVersion.objects.create(
            plugin=self.plugin,
            created_by=self.creator,
            min_qg_version="0.0.0",
            max_qg_version="99.99.99",
            version="0.2",
            approved=False,
            external_deps="test"
        )

    def test_create_feedback_success(self):
        feedback = PluginVersionFeedback.objects.create(
            version=self.version,
            reviewer=self.staff,
            task="test comment in a feedback."
        )
        self.assertIsNotNone(feedback.created_on)
        self.assertFalse(feedback.is_completed)
        self.assertIsNone(feedback.completed_on)

    @freeze_time("2023-06-30 10:00:00")
    def test_update_feedback_is_completed(self):
        feedback = PluginVersionFeedback.objects.create(
            version=self.version,
            reviewer=self.staff,
            task="test comment in a feedback.",
            is_completed=True
        )
        self.assertEqual(feedback.completed_on, datetime(2023, 6, 30, 10, 0, 0))
        feedback.is_completed = False
        feedback.save()
        self.assertIsNone(feedback.completed_on)


class PluginVersionFeedbackManagerTest(TestCase):
    fixtures = ["fixtures/auth.json", ]

    def setUp(self):
        self.creator = User.objects.get(id=2)
        self.staff = User.objects.get(id=3)
        self.plugin_1 = Plugin.objects.create(
            created_by=self.creator,
            repository="http://example.com",
            tracker="http://example.com",
            package_name="plugin-test-1",
            name="plugin test 1",
            about="this is a test for plugin feedbacks"
        )
        self.version_1 = PluginVersion.objects.create(
            plugin=self.plugin_1,
            created_by=self.creator,
            min_qg_version="0.0.0",
            max_qg_version="99.99.99",
            version="1.0",
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
            name="plugin test 2",
            about="this is a test for plugin feedbacks"
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

    def test_query_plugins_objects_all(self):
        plugins = Plugin.objects.all()
        self.assertEqual(len(plugins), 2)

    def test_query_plugins_feedback_received_objects(self):
        plugins = Plugin.feedback_received_objects.all()
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0], self.plugin_1)

        PluginVersionFeedback.objects.create(
            version=self.version_2,
            reviewer=self.staff,
            task="test comment in a feedback for plugin 2."
        )
        plugins = Plugin.feedback_received_objects.all()
        self.assertEqual(len(plugins), 2)
        self.assertListEqual(list(plugins), [self.plugin_1, self.plugin_2])


    def test_query_plugins_feedback_pending_objects(self):
        plugins = Plugin.feedback_pending_objects.all()
        self.assertEqual(len(plugins), 1)
        self.assertEqual(plugins[0], self.plugin_2)


