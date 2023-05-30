from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from plugins.models import Plugin, PluginVersion


class TestPluginVersionReview(TestCase):
    fixtures = ["fixtures/simplemenu.json", "fixtures/auth.json"]

    def setUp(self):
        self.url = reverse('version_review')
        self.creator = User.objects.get(pk=2)
        # create a plugin

    def test_plugin_detail_tab_version_manage_showing_review_icon(self):
        pass

    def test_review_page_showing_correct_button_creator_account(self):
        pass

    def test_review_page_showing_correct_button_editor_account(self):
        pass

    def test_review_page_post_comment(self):
        pass

    def test_review_page_view_comments(self):
        pass

    def tearDown(self):
        self.client.logout()
