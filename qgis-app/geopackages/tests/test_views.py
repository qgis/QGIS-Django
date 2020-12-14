import os
import tempfile

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User, Group
from geopackages.models import Geopackage, GeopackageReview

from geopackages.views import geopackage_notify, geopackage_update_notify
from geopackages.forms import GeopackageUploadForm

GPKG_DIR = os.path.join(os.path.dirname(__file__), "gpkgfiles")


class SetUpTest():
    """
    SetUp for all Test Class
    """

    def setUp(self):
        self.thumbnail = os.path.join(GPKG_DIR, "thumbnail.png")
        self.thumbnail_content = open(self.thumbnail, 'rb')
        self.gpkg_file = os.path.join(GPKG_DIR, "spiky-polygons.gpkg")
        self.gpkg_file_content = open(self.gpkg_file, 'rb')
        self.gpkg_oversize = os.path.join(GPKG_DIR, "dummy_oversize.gpkg")
        self.gpkg_oversize_content = open(self.gpkg_oversize, 'rb')

        self.creator = User.objects.create(
            username="creator", email="creator@email.com"
        )
        # set creator password to password
        self.creator.set_password("password")
        self.creator.save()
        self.staff = User.objects.create(
            username="staff", email="staff@email.com"
        )
        self.staff.set_password("password")
        self.staff.save()
        self.group = Group.objects.create(name="Style Managers")
        self.group.user_set.add(self.staff)

    def tearDown(self):
        self.thumbnail_content.close()
        self.gpkg_file_content.close()
        self.gpkg_oversize_content.close()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestFormValidation(SetUpTest, TestCase):

    def test_form_with_valid_data(self):
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_gpkg = SimpleUploadedFile(
            self.gpkg_file_content.name,
            self.gpkg_file_content.read()
        )
        form = GeopackageUploadForm(data={})
        self.assertFalse(form.is_valid())
        data = {
                "name": "spiky polygons",
                "description": "Test upload with valid data"
        }
        file_data = {
            'thumbnail_image': uploaded_thumbnail,
            'gpkg_file': uploaded_gpkg
        }
        form = GeopackageUploadForm(data, file_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_gpkg_file_extension(self):
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_gpkg = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        data = {
                "name": "spiky polygons",
                "description": "Test upload invalid gpkg file extension"
        }
        file_data = {
            'thumbnail_image': uploaded_thumbnail,
            'gpkg_file': uploaded_gpkg
        }
        form = GeopackageUploadForm(data, file_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
                         {'gpkg_file': ['The submitted file is empty.']})

    def test_form_invalid_gpkg_filesize(self):
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_gpkg = SimpleUploadedFile(
            self.gpkg_oversize_content.name,
            self.gpkg_oversize_content.read()
        )
        data = {
                'name': 'spiky polygons',
                'description': 'Test upload invalid gpkg filesize'
        }
        file_data = {
            'thumbnail_image': uploaded_thumbnail,
            'gpkg_file': uploaded_gpkg
        }
        form = GeopackageUploadForm(data, file_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {'gpkg_file': ['File is too big. Max size is 1.0 Megabytes']}
        )


@override_settings(MEDIA_ROOT="geopackages/tests/gpkgfiles/")
class TestEmailNotification(SetUpTest, TestCase):
    """
    Send the email to console
    """

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_print_email_notification_in_console(self):
        Geopackage.objects.create(
            creator=self.creator,
            name="spiky polygons",
            description="A GeoPackage for testing purpose",
            thumbnail_image=self.thumbnail,
            gpkg_file=self.gpkg_file
        )
        gpkg = Geopackage.objects.first()
        geopackage_notify(gpkg)
        GeopackageReview.objects.create(
            reviewer=self.staff,
            geopackage=gpkg,
            comment="Rejected for testing purpose")
        gpkg.require_action = True
        gpkg.save()
        geopackage_update_notify(gpkg, self.creator, self.staff)
        GeopackageReview.objects.create(
            reviewer=self.staff,
            geopackage=gpkg,
            comment="Approved! This is for testing purpose")
        gpkg.approved = True
        gpkg.save()
        geopackage_update_notify(gpkg, self.creator, self.staff)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestUploadGeoPackage(SetUpTest, TestCase):

    def test_upload_acceptable_size_file(self):
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("geopackage_create")
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_gpkg = SimpleUploadedFile(
            self.gpkg_file_content.name,
            self.gpkg_file_content.read()
        )
        data = {
            "name": "spiky polygons",
            "description": "Test upload an acceptable gpkg size",
            "thumbnail_image": uploaded_thumbnail,
            "gpkg_file": uploaded_gpkg
        }
        response = self.client.post(url, data, follow=True)
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        gpkg = Geopackage.objects.first()
        self.assertEqual(gpkg.name, "spiky polygons")
        url = reverse("geopackage_detail", kwargs={'pk': gpkg.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_upload_invalid_size_file(self):
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("geopackage_create")
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_gpkg = SimpleUploadedFile(
            self.gpkg_oversize_content.name,
            self.gpkg_oversize_content.read()
        )
        data = {
            "name": "spiky polygons",
            "description": "Test upload a gpkg > 1Mb filesize",
            "thumbnail_image": uploaded_thumbnail,
            "gpkg_file": uploaded_gpkg
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Should not create new object
        gpkg = Geopackage.objects.first()
        self.assertIsNone(gpkg)


@override_settings(MEDIA_ROOT="geopackages/tests/gpkgfiles/")
class TestReviewGeopackage(SetUpTest, TestCase):

    def setUp(self):
        super(TestReviewGeopackage, self).setUp()
        self.gpkg_object = Geopackage.objects.create(
            creator=self.creator,
            name="spiky polygons",
            description="A GeoPackage for testing purpose",
            thumbnail_image=self.thumbnail,
            gpkg_file=self.gpkg_file
        )

    def test_review_should_be_done_by_staff(self):
        url = reverse('geopackage_review', kwargs={'pk': self.gpkg_object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_approve_gpkg(self):
        login = self.client.login(username="staff", password="password")
        self.assertTrue(login)
        url = reverse('geopackage_review', kwargs={'pk': self.gpkg_object.id})
        response = self.client.post(url, {
            'approval': 'approve',
            'comment': 'This should be in Approve page.'
        })
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        url = reverse('geopackage_detail', kwargs={'pk': self.gpkg_object.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'This should be in Approve page.')
        self.assertContains(response, 'Approved Date')
        self.client.logout()

    def test_reject_gpkg(self):
        login = self.client.login(username="staff", password="password")
        self.assertTrue(login)
        url = reverse('geopackage_review', kwargs={'pk': self.gpkg_object.id})
        response = self.client.post(url, {
            'approval': 'reject',
            'comment': 'This should be in requiring update page.'
        })
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        url = reverse('geopackage_detail', kwargs={'pk': self.gpkg_object.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            'This should be in requiring update page.')
        self.assertContains(response, 'Reviewed by Staff now')
        self.client.logout()
        # creator should find the rejected styles in requiring update page
        self.client.login(username="creator", password="password")
        url = reverse('geopackage_require_action')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 record found.")
        self.assertContains(response, "spiky polygons")
