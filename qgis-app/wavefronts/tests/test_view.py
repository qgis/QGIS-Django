import io
import os
import tempfile
import zipfile

from django.contrib.auth.models import Group, User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from wavefronts.models import Wavefront

WAVEFRONT_DIR = os.path.join(os.path.dirname(__file__), "wavefrontfiles")


class SetUpTest:
    """
    SetUp for all Test Class
    """

    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        self.thumbnail = os.path.join(WAVEFRONT_DIR, "thumbnail.png")
        self.thumbnail_content = open(self.thumbnail, "rb")
        self.zipfile = os.path.join(WAVEFRONT_DIR, "odm_texturing_25d.zip")
        self.zipfile_content = open(self.zipfile, "rb")

        self.creator = User.objects.create(
            username="creator", email="creator@email.com"
        )
        # set creator password to password
        self.creator.set_password("password")
        self.creator.save()
        self.staff = User.objects.create(username="staff", email="staff@email.com")
        self.staff.set_password("password")
        self.staff.save()
        self.group = Group.objects.create(name="Style Managers")
        self.group.user_set.add(self.staff)

    def tearDown(self):
        self.thumbnail_content.close()
        self.zipfile_content.close()


class TestPageUserAnonymous(TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def test_url(self):
        url = reverse("wavefront_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "All 3D Models")
        self.assertContains(response, "No data.")

    def test_upload(self):
        url = reverse("wavefront_create")
        response = self.client.get(url)
        self.assertRedirects(response, "/accounts/login/?next=/wavefronts/add/")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestReviewWavefront(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestReviewWavefront, self).setUp()
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("wavefront_create")
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name, self.thumbnail_content.read()
        )
        uploaded_file = SimpleUploadedFile(
            self.zipfile_content.name, self.zipfile_content.read()
        )
        data = {
            "name": "odm texturing",
            "description": "Test upload a wavefront",
            "thumbnail_image": uploaded_thumbnail,
            "file": uploaded_file,
        }
        self.client.post(url, data, follow=True)
        self.object = Wavefront.objects.first()
        self.client.logout()

    def test_approve_wavefront(self):
        login = self.client.login(username="staff", password="password")
        self.assertTrue(login)
        url = reverse("wavefront_review", kwargs={"pk": self.object.id})
        response = self.client.post(
            url, {"approval": "approve", "comment": "This should be in Approve page."}
        )
        # should send email notify
        self.assertIn(
            "\n3D Model odm texturing approved by staff."
            "\nThis should be in Approve page.",
            mail.outbox[-1].body,
        )
        url = reverse("wavefront_detail", kwargs={"pk": self.object.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "This should be in Approve page.")
        self.assertContains(response, "Approved Date")
        self.client.logout()

    def test_reject_model(self):
        login = self.client.login(username="staff", password="password")
        self.assertTrue(login)
        url = reverse("wavefront_review", kwargs={"pk": self.object.id})
        response = self.client.post(
            url,
            {
                "approval": "reject",
                "comment": "This should be in requiring update page.",
            },
        )
        # should send email notify
        self.assertIn(
            "\n3D Model odm texturing rejected by staff."
            "\nThis should be in requiring update page.",
            mail.outbox[-1].body,
        )
        url = reverse("wavefront_detail", kwargs={"pk": self.object.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This should be in requiring update page.")
        self.assertContains(response, "Reviewed by Staff now")
        self.client.logout()
        # creator should find the rejected styles in requiring update page
        self.client.login(username="creator", password="password")
        url = reverse("wavefront_require_action")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 record found.")
        self.assertContains(response, "odm texturing")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestDownloadWavefront(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TestDownloadWavefront, self).setUp()
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("wavefront_create")
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name, self.thumbnail_content.read()
        )
        uploaded_file = SimpleUploadedFile(
            self.zipfile_content.name, self.zipfile_content.read()
        )
        data = {
            "name": "odm texturing",
            "description": "Test upload a wavefront",
            "thumbnail_image": uploaded_thumbnail,
            "file": uploaded_file,
        }
        self.client.post(url, data, follow=True)
        self.object = Wavefront.objects.first()
        self.client.logout()

    def test_download_should_return_zipfile(self):
        wavefront = Wavefront.objects.last()
        wavefront.approved = True
        wavefront.save()
        url = reverse("wavefront_download", kwargs={"pk": wavefront.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(
            response.get("Content-Disposition"),
            "attachment; filename=odm-texturing.zip",
        )
        expected_filename_list = [
            "odm texturing/odm_textured_model_geo.mtl",
            "odm texturing/odm_textured_model_geo_material0000_map_Kd.png",
            "odm texturing/odm_textured_model.mtl",
            "odm texturing/odm_textured_model_geo.conf",
            "odm texturing/odm_textured_model_geo.obj",
            "odm texturing/license.txt",
        ]
        with io.BytesIO(response.content) as file:
            zip_file = zipfile.ZipFile(file, "r")
            self.assertIsNone(zip_file.testzip())
            for f in expected_filename_list:
                self.assertIn(f, zip_file.namelist())
            self.assertNotIn(
                "odm texturing/odm_textured_model_geo.zip", zip_file.namelist()
            )
            zip_file.close()
