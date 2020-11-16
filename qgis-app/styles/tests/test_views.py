import os
import tempfile

from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from django.contrib.auth.models import User
from styles.models import Style, StyleType

STYLE_DIR = os.path.join(os.path.dirname(__file__), "stylefiles")


class TestPageUserAnonymous(TestCase):
    def test_url(self):
        url = reverse('style_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Styles")
        self.assertContains(response, "Style Type")
        self.assertContains(response, "No data.")

    def test_upload(self):
        url = reverse('style_create')
        response = self.client.get(url)
        self.assertRedirects(response, '/accounts/login/?next=/styles/add/')


class TestUploadStyle(TestCase):
    fixtures = ['fixtures/auth.json']

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def setUp(self):
        self.thumbnail = os.path.join(STYLE_DIR, "thumbnail.png")
        self.creator = User.objects.get(pk=2)
        # set creator password to password
        self.creator.set_password("password")
        self.creator.save()
        # user is logging in to upload page
        self.client.login(username="creator", password="password")
        url = reverse('style_create')
        self.response = self.client.get(url)

    def test_upload_page_with_login(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'styles/style_form.html')
        self.assertContains(self.response, "To upload a new style, "
            "you can specify the xml file in this form.")

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_upload_xml_file(self):
        url = reverse('style_create')
        f = os.path.join(STYLE_DIR, "cattrail.xml")
        with open(f) as xml_file:
            self.client.post(url, {
                'xml_file': xml_file,
                'thumbnail_image': self.thumbnail,
                'description': 'This style is for testing only purpose'
            })
        self.assertEqual(self.response.status_code, 200)
        # style should be in Waiting Review
        url = reverse('style_unapproved')
        self.response = self.client.get(url)
        self.assertContains(self.response, "1 record found.")
        self.assertContains(self.response, "Cat Trail")
        self.assertContains(self.response, "Line")
        self.assertContains(self.response, "Creator")
        # style should not be in Requiring Update
        url = reverse('style_require_action')
        self.response = self.client.get(url)
        self.assertContains(self.response, "No data.")


class TestModeration(TestCase):
    fixtures = ['fixtures/auth.json']

    @classmethod
    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def setUpTestData(cls):
        cls.thumbnail = os.path.join(STYLE_DIR, "thumbnail.png")
        cls.creator = User.objects.get(pk=2)
        # set creator's password to password
        cls.creator.set_password("password")
        cls.creator.save()
        cls.staff = User.objects.get(pk=3)
        # set staff's password to password
        cls.staff.set_password("password")
        cls.staff.save()
        # upload a style xml
        c = Client()
        c.login(username="creator", password="password")
        url = reverse('style_create')
        f = os.path.join(STYLE_DIR, "legend_patch.xml")
        with open(f) as xml_file:
            c.post(url, {
                'xml_file': xml_file,
                'thumbnail_image': cls.thumbnail,
                'description': 'This style is for testing only purpose'
            })
        c.logout()
        cls.uploaded_style = Style.objects.filter(name="Building 3").first()

    def setUp(self):
        self._original_media_root = settings.MEDIA_ROOT
        self._temp_media = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self._temp_media

    def tearDown(self):
        settings.MEDIA_ROOT = self._original_media_root

    def test_user_anonymous_should_not_see_moderation_link(self):
        url = reverse('style_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Styles")
        self.assertNotContains(response, "Waiting Review")
        self.assertNotContains(response, "Requiring Update")

    def test_user_anonymous_should_redirect_from_moderation(self):
        url = reverse('style_unapproved')
        response = self.client.get(url)
        self.assertRedirects(response,
            '/accounts/login/?next=/styles/unapproved/')
        url = reverse('style_require_action')
        response = self.client.get(url)
        self.assertRedirects(response,
            '/accounts/login/?next=/styles/require_action/')

    def test_creator_should_see_moderation_list(self):
        self.client.login(username="creator", password="password")
        url = reverse('style_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Styles")
        self.assertContains(response, "Waiting Review")
        # go to waiting review page
        url = reverse('style_unapproved')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 record found.")
        self.assertContains(response, "Building 3")
        self.assertContains(response, "Legendpatchshape")
        # do detail review
        url = reverse('style_detail', kwargs={'pk': self.uploaded_style.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Building 3")
        self.assertContains(response, "in review")
        self.assertNotContains(response, '<textarea name="comment"')
        self.assertNotContains(response, '<input type="submit" '
            'class="btn btn-primary" value="Submit Review">', html=True)
        # go to requiring update page
        url = reverse('style_require_action')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No data.")

    def test_another_user_should_not_see_moderation_list(self):
        newuser = User.objects.create(
            username='newuser',
            email='newuser@email.com',
            is_staff=False
        )
        newuser.set_password("password")
        newuser.save()
        # go to waiting review page
        self.client.login(username="newuser", password="password")
        url = reverse('style_unapproved')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No data.")
        self.client.logout()

    def test_staff_should_see_moderation_detail(self):
        self.client.login(username="staff", password="password")
        url = reverse('style_detail', kwargs={'pk': self.uploaded_style.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<textarea name="comment"')
        self.assertContains(response, '<input type="submit" '
            'class="btn btn-primary" value="Submit Review">', html=True)
        self.client.logout()

    def test_staff_reject_and_submit_comment(self):
        self.client.login(username="staff", password="password")
        url = reverse('style_review', kwargs={'pk': self.uploaded_style.id})
        response = self.client.post(url, {
            'approval': 'reject',
            'comment' : 'This should be in requiring update page.'
        })
        url = reverse('style_detail', kwargs={'pk': self.uploaded_style.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
            'This should be in requiring update page.')
        self.assertContains(response, 'Reviewed by Staff now')
        self.client.logout()
        # creator should find the rejected styles in requiring update page
        self.client.login(username="creator", password="password")
        url = reverse('style_require_action')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Building 3')

    def test_staff_approve(self):
        self.client.login(username="staff", password="password")
        url = reverse('style_review', kwargs={'pk': self.uploaded_style.id})
        response = self.client.post(url, {
            'approval': 'approve',
            'comment': 'This should be in Approve page.'
        })
        url = reverse('style_detail', kwargs={'pk': self.uploaded_style.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'This should be in Approve page.')
        self.assertContains(response, 'Approved Date')
        self.client.logout()

    def test_anonymous_should_see_approved_styles(self):
        self.uploaded_style.approved = True
        self.uploaded_style.save()
        url = reverse('style_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All Styles")
        self.assertContains(response, "1 record found.")
        self.assertContains(response, "Creator")


class TestDownloadStyles(TestCase):
    fixtures = ['fixtures/auth.json']

    def setUp(self):
        StyleType.objects.create(
            pk=1,
            symbol_type="line",
            name="Line",
            description="For testing purpose only.")
        self.newstyle = Style.objects.create(
            pk=1,
            creator=User.objects.get(pk=2),
            style_type=StyleType.objects.get(pk=1),
            name="Blues",
            description="This file is saved in styles/tests/stylefiles folder",
            thumbnail_image="thumbnail.png",
            xml_file="colorramp_blue.xml",
            download_count=0,
            approved=True,
        )

    @override_settings(MEDIA_ROOT="styles/tests/stylefiles/")
    def test_anonymous_user_download(self):
        style = Style.objects.get(pk=1)
        self.assertEqual(style.download_count, 0)
        self.client.logout()
        url = reverse('style_download', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # download_count should be increased
        style = Style.objects.get(pk=1)
        self.assertEqual(style.download_count, 1)
