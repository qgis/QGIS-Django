import os
import tempfile

from django.conf import settings
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from django.contrib.auth.models import User
from geopackages.models import Geopackage, GeopackageReview

GPKG_DIR = os.path.join(os.path.dirname(__file__), "gpkgfiles")


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
class TestUpload(TestCase):

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def setUp(self):
        self.thumbnail = os.path.join(GPKG_DIR, "thumbnail.png")
        self.creator = User.objects.create(
            username="creator", email="creator@email.com"
        )
        # set creator password to password
        self.creator.set_password("password")
        self.creator.save()
        # user is logging in to upload page
        self.client.login(username="creator", password="password")
        url = reverse('geopackage_create')
        self.response = self.client.get(url)

    def test_upload_page_with_login(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, 'geopackages/geopackage_form.html')

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_upload_xml_file(self):
        url = reverse('geopackage_create')
        f = os.path.join(GPKG_DIR, "spiky-polygons.gpkg")
        self.client.post(url, {
                'gpkg_file': f,
                'thumbnail_image': self.thumbnail,
                'name': 'spiky polygons',
                'description': 'This style is for testing only purpose'
            })
        self.assertEqual(self.response.status_code, 200)
        # style should be in Waiting Review
        url = reverse('geopackage_unapproved')
        self.response = self.client.get(url)
        self.assertEqual(self.response, "1 record found.")
        self.assertContains(self.response, "1 record found.")
        # style should not be in Requiring Update
        url = reverse('geopackage_require_action')
        self.response = self.client.get(url)
        self.assertContains(self.response, "No data.")

