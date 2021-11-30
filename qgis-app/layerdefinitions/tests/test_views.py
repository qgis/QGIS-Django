import io
import os
import tempfile
import zipfile

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User, Group
from layerdefinitions.models import LayerDefinition

TESTFILES_DIR = os.path.join(os.path.dirname(__file__), 'testfiles')


class SetUpTest():
    """SetUp for all Test Class"""

    fixtures = ['fixtures/simplemenu.json']

    def setUp(self):
        self.thumbnail = os.path.join(TESTFILES_DIR, 'thumbnail.png')
        self.thumbnail_content = open(self.thumbnail, 'rb')
        self.file = os.path.join(TESTFILES_DIR, 'my-vapour-pressure.qlr')
        self.file_content = open(self.file, 'rb')

        self.creator = User.objects.create(
            username='creator', email='creator@email.com'
        )
        # set creator password to password
        self.creator.set_password('password')
        self.creator.save()
        self.staff = User.objects.create(
            username='staff', email='staff@email.com'
        )
        self.staff.set_password('password')
        self.staff.save()
        self.group = Group.objects.create(name='Style Managers')
        self.group.user_set.add(self.staff)

    def tearDown(self):
        self.thumbnail_content.close()
        self.file_content.close()


class TestPageUserAnonymous(TestCase):
    fixtures = ['fixtures/simplemenu.json']

    def test_url(self):
        url = reverse('layerdefinition_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'All Layer Definition Files')
        self.assertContains(response, 'No data.')

    def test_upload(self):
        url = reverse('layerdefinition_create')
        response = self.client.get(url)
        self.assertRedirects(
            response,
            '/accounts/login/?next=/layerdefinitions/add/'
        )


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestUploadLayerDefinitionFile(SetUpTest, TestCase):
    fixtures = ['fixtures/simplemenu.json']

    def setUp(self):
        super(TestUploadLayerDefinitionFile, self).setUp()
        login = self.client.login(username='creator', password='password')
        self.assertTrue(login)
        url = reverse('layerdefinition_create')
        self.uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        self.uploaded_file = SimpleUploadedFile(
            self.file_content.name,
            self.file_content.read()
        )
        self.data = {
            'name': 'Test QLR File',
            'description': 'Test upload a QLR File',
            'thumbnail_image': self.uploaded_thumbnail,
            'file': self.uploaded_file,
            'license': 'license'
        }
        self.response = self.client.post(url, self.data, follow=True)

    def test_upload_file_succeed_send_notification(self):
        self.assertEqual(self.response.status_code, 200)
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            mail.outbox[0].subject,
            'A new Layer Definition File has been created by creator.'
        )

    def test_uploaded_file_create_model_instance(self):
        qlr = LayerDefinition.objects.first()
        self.assertEqual(qlr.name, self.data['name'])
        self.assertEqual(qlr.description, self.data['description'])
        self.assertEqual(qlr.approved, False)
        self.assertEqual(qlr.license, self.data['license'])
        self.assertEqual(qlr.provider, 'wms')
        self.assertEqual(
            qlr.url_datasource,
            'https://maps.kartoza.com/geoserver/kartoza/wms'
        )


@override_settings(MEDIA_ROOT="layerdefinitions/tests/testfiles/")
class TestReviewLayerDefinition(SetUpTest, TestCase):
    fixtures = ['fixtures/simplemenu.json']

    def setUp(self):
        super(TestReviewLayerDefinition, self).setUp()
        self.qlr_object = LayerDefinition.objects.create(
            creator=self.creator,
            name='Test QLR File',
            description='A QLR file for testing purpose',
            thumbnail_image=self.thumbnail,
            file=self.file
        )

    def test_approval_layerdefinition_flow_approved(self):
        login = self.client.login(username='staff', password='password')
        self.assertTrue(login)
        url = reverse(
            'layerdefinition_review',
            kwargs={'pk': self.qlr_object.id}
        )
        response = self.client.post(url, {
            'approval': 'approve',
            'comment': 'This should be in qlr approval page.'
        })
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        url = reverse(
            'layerdefinition_detail',
            kwargs={'pk': self.qlr_object.id}
        )
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            'This should be in qlr approval page.'
        )
        self.assertContains(response, 'Approved Date')
        self.client.logout()

    def test_approval_layerdefinition_flow_rejected(self):
        login = self.client.login(username="staff", password="password")
        self.assertTrue(login)
        url = reverse(
            'layerdefinition_review',
            kwargs={'pk': self.qlr_object.id}
        )
        response = self.client.post(url, {
            'approval': 'reject',
            'comment': 'This should be in requiring update page.'
        })
        # should send email notify
        self.assertEqual(len(mail.outbox), 1)
        url = reverse(
            'layerdefinition_detail',
            kwargs={'pk': self.qlr_object.id}
        )
        self.assertRedirects(response, url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'This should be in requiring update page.'
        )
        self.assertContains(response, 'Reviewed by Staff now')
        self.client.logout()
        # creator should find the rejected styles in requiring update page
        self.client.login(username="creator", password="password")
        url = reverse('layerdefinition_require_action')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 record found.")
        self.assertContains(response, "Test QLR File")


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestDownloadLayerDefinition(SetUpTest, TestCase):
    fixtures = ['fixtures/simplemenu.json']

    def setUp(self):
        super(TestDownloadLayerDefinition, self).setUp()
        self.client.login(username='creator', password='password')
        url = reverse('layerdefinition_create')
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name,
            self.thumbnail_content.read()
        )
        uploaded_file = SimpleUploadedFile(
            self.file_content.name,
            self.file_content.read()
        )
        data = {
            'name': 'Test QLR File',
            'description': 'Test upload a QLR File',
            'thumbnail_image': uploaded_thumbnail,
            'file': uploaded_file,
            'license': 'license'
        }
        self.client.post(url, data, follow=True)

    def test_download_should_return_zipfile_with_custom_license(self):
        qlr = LayerDefinition.objects.last()
        qlr.approved = True
        qlr.save()
        url = reverse('layerdefinition_download', kwargs={'pk': qlr.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEquals(
            response.get('Content-Disposition'),
            'attachment; filename=test-qlr-file.zip'
        )
        expected_filename_list = [
            'Test QLR File/my-vapour-pressure.qlr',
            'Test QLR File/license.txt'
        ]
        with io.BytesIO(response.content) as file:
            zip_file = zipfile.ZipFile(file, 'r')
            self.assertIsNone(zip_file.testzip())
            for f in expected_filename_list:
                self.assertIn(f, zip_file.namelist())
            zip_file.close()
