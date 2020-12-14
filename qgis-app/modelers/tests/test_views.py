import os
import tempfile

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User, Group
from modelers.models import Modeler, ModelerReview

from modelers.views import modeler_notify, modeler_update_notify
from modelers.forms import ModelerUploadForm

MODEL_DIR = os.path.join(os.path.dirname(__file__), "modelfiles")


class SetUpTest():
    """
    SetUp for all Test Class
    """

    def setUp(self):
        self.thumbnail = os.path.join(MODEL_DIR, "thumbnail.png")
        self.thumbnail_content = open(self.thumbnail, 'rb')
        self.model_file = os.path.join(MODEL_DIR,
                                       "flooded-buildings-extractor.model3")
        self.model_file_content = open(self.model_file, 'rb')
        self.modelzip_file = os.path.join(MODEL_DIR,
                                       "flooded-buildings-extractor.zip")
        self.modelzip_file_content = open(self.modelzip_file, 'rb')
        self.model_oversize = os.path.join(MODEL_DIR, "dummy_oversize.model3")
        self.model_oversize_content = open(self.model_oversize, 'rb')

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
        self.model_file_content.close()
        self.modelzip_file_content.close()
        self.model_oversize_content.close()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestFormValidation(SetUpTest, TestCase):

    def test_form_with_valid_data(self):
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_model = SimpleUploadedFile(
            self.model_file_content.name,
            self.model_file_content.read()
        )
        form = ModelerUploadForm(data={})
        self.assertFalse(form.is_valid())
        data = {
                "name": "flooded building extractor",
                "description": "Test upload with valid data"
        }
        file_data = {
            'thumbnail_image': uploaded_thumbnail,
            'model_file': uploaded_model
        }
        form = ModelerUploadForm(data, file_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_model_file_extension(self):
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_model = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        data = {
                "name": "flooded buildings extractor",
                "description": "Test upload invalid model file extension"
        }
        file_data = {
            'thumbnail_image': uploaded_thumbnail,
            'model_file': uploaded_model
        }
        form = ModelerUploadForm(data, file_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
                         {'model_file': ['The submitted file is empty.']})

    def test_form_invalid_model_filesize(self):
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_model = SimpleUploadedFile(
            self.model_oversize_content.name,
            self.model_oversize_content.read()
        )
        data = {
                'name': 'flooded buildings extractor',
                'description': 'Test upload invalid model filesize'
        }
        file_data = {
            'thumbnail_image': uploaded_thumbnail,
            'model_file': uploaded_model
        }
        form = ModelerUploadForm(data, file_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {'model_file': ['File is too big. Max size is 1.0 Megabytes']}
        )


@override_settings(MEDIA_ROOT="modelers/tests/modelfiles/")
class TestEmailNotification(SetUpTest, TestCase):
    """
    Send the email to console
    """

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_print_email_notification_in_console(self):
        Modeler.objects.create(
            creator=self.creator,
            name="flooded buildings extractor",
            description="A Model for testing purpose",
            thumbnail_image=self.thumbnail,
            model_file=self.model_file
        )
        model = Modeler.objects.first()
        modeler_notify(model)
        ModelerReview.objects.create(
            reviewer=self.staff,
            modeler=model,
            comment="Rejected for testing purpose")
        model.require_action = True
        model.save()
        modeler_update_notify(model, self.creator, self.staff)
        ModelerReview.objects.create(
            reviewer=self.staff,
            modeler=model,
            comment="Approved! This is for testing purpose")
        model.approved = True
        model.save()
        modeler_update_notify(model, self.creator, self.staff)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestUploadModel(SetUpTest, TestCase):

    def test_upload_acceptable_model3_size_file(self):
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("modeler_create")
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_model = SimpleUploadedFile(
            self.model_file_content.name,
            self.model_file_content.read()
        )
        data = {
            "name": "flooded buildings extractor",
            "description": "Test upload an acceptable model size",
            "thumbnail_image": uploaded_thumbnail,
            "model_file": uploaded_model
        }
        response = self.client.post(url, data, follow=True)
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        model = Modeler.objects.first()
        self.assertEqual(model.name, "flooded buildings extractor")
        url = reverse("modeler_detail", kwargs={'pk': model.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_upload_acceptable_zip_size_file(self):
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("modeler_create")
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_model = SimpleUploadedFile(
            self.modelzip_file_content.name,
            self.modelzip_file_content.read()
        )
        data = {
            "name": "flooded buildings extractor",
            "description": "Test upload .zip model",
            "thumbnail_image": uploaded_thumbnail,
            "model_file": uploaded_model
        }
        response = self.client.post(url, data, follow=True)
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        model = Modeler.objects.first()
        self.assertEqual(model.name, "flooded buildings extractor")
        url = reverse("modeler_detail", kwargs={'pk': model.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_upload_invalid_size_file(self):
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("modeler_create")
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_model = SimpleUploadedFile(
            self.model_oversize_content.name,
            self.model_oversize_content.read()
        )
        data = {
            "name": "flooded buildings extractor",
            "description": "Test upload a model > 1Mb filesize",
            "thumbnail_image": uploaded_thumbnail,
            "model_file": uploaded_model
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Should not create new object
        model = Modeler.objects.first()
        self.assertIsNone(model)


@override_settings(MEDIA_ROOT="modelers/tests/modelfiles/")
class TestReviewModeler(SetUpTest, TestCase):

    def setUp(self):
        super(TestReviewModeler, self).setUp()
        self.model_object = Modeler.objects.create(
            creator=self.creator,
            name="flooded buildings extractor",
            description="A Model for testing purpose",
            thumbnail_image=self.thumbnail,
            model_file=self.model_file
        )

    def test_review_should_be_done_by_staff(self):
        url = reverse('modeler_review', kwargs={'pk': self.model_object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_approve_model(self):
        login = self.client.login(username="staff", password="password")
        self.assertTrue(login)
        url = reverse('modeler_review', kwargs={'pk': self.model_object.id})
        response = self.client.post(url, {
            'approval': 'approve',
            'comment': 'This should be in Approve page.'
        })
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        url = reverse('modeler_detail', kwargs={'pk': self.model_object.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'This should be in Approve page.')
        self.assertContains(response, 'Approved Date')
        self.client.logout()

    def test_reject_model(self):
        login = self.client.login(username="staff", password="password")
        self.assertTrue(login)
        url = reverse('modeler_review', kwargs={'pk': self.model_object.id})
        response = self.client.post(url, {
            'approval': 'reject',
            'comment': 'This should be in requiring update page.'
        })
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        url = reverse('modeler_detail', kwargs={'pk': self.model_object.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            'This should be in requiring update page.')
        self.assertContains(response, 'Reviewed by Staff now')
        self.client.logout()
        # creator should find the rejected styles in requiring update page
        self.client.login(username="creator", password="password")
        url = reverse('modeler_require_action')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 record found.")
        self.assertContains(response, "flooded buildings extractor")
