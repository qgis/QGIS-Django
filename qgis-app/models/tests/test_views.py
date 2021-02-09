import os
import tempfile

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User, Group
from models.models import Model, Review

from base.views.processing_view import resource_notify, resource_update_notify
from models.forms import UploadForm

MODEL_DIR = os.path.join(os.path.dirname(__file__), "modelfiles")


class SetUpTest():
    """
    SetUp for all Test Class
    """

    fixtures = ['fixtures/simplemenu.json']

    def setUp(self):
        self.thumbnail = os.path.join(MODEL_DIR, "thumbnail.png")
        self.thumbnail_content = open(self.thumbnail, 'rb')
        self.file = os.path.join(MODEL_DIR,
                                       "example.model3")
        self.file_content = open(self.file, 'rb')
        self.modelzip_file = os.path.join(MODEL_DIR,
                                       "example.zip")
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
        self.file_content.close()
        self.modelzip_file_content.close()
        self.model_oversize_content.close()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestFormValidation(SetUpTest, TestCase):
    fixtures = ['fixtures/simplemenu.json']

    def test_form_with_valid_data(self):
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_model = SimpleUploadedFile(
            self.file_content.name,
            self.file_content.read()
        )
        form = UploadForm(data={})
        self.assertFalse(form.is_valid())
        data = {
                "name": "flooded building extractor",
                "description": "Test upload with valid data"
        }
        file_data = {
            'thumbnail_image': uploaded_thumbnail,
            'file': uploaded_model
        }
        form = UploadForm(data, file_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_file_extension(self):
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
            'file': uploaded_model
        }
        form = UploadForm(data, file_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors,
                         {'file': ['The submitted file is empty.']})

    def test_form_invalid_filesize(self):
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
            'file': uploaded_model
        }
        form = UploadForm(data, file_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors,
            {'file': ['File is too big. Max size is 1.0 Megabytes']}
        )


@override_settings(MEDIA_ROOT="models/tests/modelfiles/")
class TestEmailNotification(SetUpTest, TestCase):
    """
    Send the email to console
    """

    fixtures = ['fixtures/simplemenu.json']

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend')
    def test_print_email_notification_in_console(self):
        Model.objects.create(
            creator=self.creator,
            name="flooded buildings extractor",
            description="A Model for testing purpose",
            thumbnail_image=self.thumbnail,
            file=self.file
        )
        model = Model.objects.first()
        resource_notify(model, resource_type='Model')
        Review.objects.create(
            reviewer=self.staff,
            resource=model,
            comment="Rejected for testing purpose")
        model.require_action = True
        model.save()
        resource_update_notify(model, self.creator, self.staff,
                               resource_type='Model')
        Review.objects.create(
            reviewer=self.staff,
            resource=model,
            comment="Approved! This is for testing purpose")
        model.approved = True
        model.save()
        resource_update_notify(model, self.creator, self.staff,
                            resource_type='Model')


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestUploadModel(SetUpTest, TestCase):
    fixtures = ['fixtures/simplemenu.json']

    def test_upload_acceptable_model3_size_file(self):
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("model_create")
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_model = SimpleUploadedFile(
            self.file_content.name,
            self.file_content.read()
        )
        data = {
            "name": "flooded buildings extractor",
            "description": "Test upload an acceptable model size",
            "thumbnail_image": uploaded_thumbnail,
            "file": uploaded_model
        }
        response = self.client.post(url, data, follow=True)
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        model = Model.objects.first()
        self.assertEqual(model.name, "flooded buildings extractor")
        url = reverse("model_detail", kwargs={'pk': model.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_upload_acceptable_zip_size_file(self):
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("model_create")
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
            "file": uploaded_model
        }
        response = self.client.post(url, data, follow=True)
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        model = Model.objects.first()
        self.assertEqual(model.name, "flooded buildings extractor")
        url = reverse("model_detail", kwargs={'pk': model.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_upload_invalid_size_file(self):
        login = self.client.login(username="creator", password="password")
        self.assertTrue(login)
        url = reverse("model_create")
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
            "file": uploaded_model
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        # Should not create new object
        model = Model.objects.first()
        self.assertIsNone(model)


@override_settings(MEDIA_ROOT="models/tests/modelfiles/")
class TestReviewModel(SetUpTest, TestCase):
    fixtures = ['fixtures/simplemenu.json']

    def setUp(self):
        super(TestReviewModel, self).setUp()
        self.model_object = Model.objects.create(
            creator=self.creator,
            name="flooded buildings extractor",
            description="A Model for testing purpose",
            thumbnail_image=self.thumbnail,
            file=self.file
        )

    def test_approve_model(self):
        login = self.client.login(username="staff", password="password")
        self.assertTrue(login)
        url = reverse('model_review', kwargs={'pk': self.model_object.id})
        response = self.client.post(url, {
            'approval': 'approve',
            'comment': 'This should be in Approve page.'
        })
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        url = reverse('model_detail', kwargs={'pk': self.model_object.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'This should be in Approve page.')
        self.assertContains(response, 'Approved Date')
        self.client.logout()

    def test_reject_model(self):
        login = self.client.login(username="staff", password="password")
        self.assertTrue(login)
        url = reverse('model_review', kwargs={'pk': self.model_object.id})
        response = self.client.post(url, {
            'approval': 'reject',
            'comment': 'This should be in requiring update page.'
        })
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        url = reverse('model_detail', kwargs={'pk': self.model_object.id})
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
                            'This should be in requiring update page.')
        self.assertContains(response, 'Reviewed by Staff now')
        self.client.logout()
        # creator should find the rejected styles in requiring update page
        self.client.login(username="creator", password="password")
        url = reverse('model_require_action')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 record found.")
        self.assertContains(response, "flooded buildings extractor")
