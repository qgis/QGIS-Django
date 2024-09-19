
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from geopackages.models import Geopackage
from layerdefinitions.models import LayerDefinition
from django.urls import reverse
from models.models import Model
from styles.models import Style
import os
import tempfile
from django.test import override_settings
from os.path import dirname, join
from django.core.files.uploadedfile import SimpleUploadedFile
from wavefronts.models import Wavefront

GPKG_DIR = join(dirname(dirname(dirname(__file__))), "geopackages", "tests", "gpkgfiles")
LAYERDEFINITION_DIR = join(dirname(dirname(dirname(__file__))), "layerdefinitions", "tests", "testfiles")
MODELS_DIR = join(dirname(dirname(dirname(__file__))), "models", "tests", "modelfiles")
STYLES_DIR = join(dirname(dirname(dirname(__file__))), "styles", "tests", "stylefiles")
WAVEFRONT_DIR = join(dirname(dirname(dirname(__file__))), "wavefronts", "tests", "wavefrontfiles")


class SetUpTest:
    """
    SetUp for all Test Class
    """

    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        self.thumbnail = join(GPKG_DIR, "thumbnail.png")
        self.thumbnail_content = open(self.thumbnail, "rb")
        self.gpkg_file = join(GPKG_DIR, "spiky-polygons.gpkg")
        self.gpkg_file_content = open(self.gpkg_file, "rb")
        self.qlr_file = join(LAYERDEFINITION_DIR, "my-vapour-pressure.qlr")
        self.qlr_file_content = open(self.qlr_file, "rb")
        self.modelzip_file = join(MODELS_DIR, "example.zip")
        self.modelzip_file_content = open(self.modelzip_file, "rb")
        self.stylexml_file = join(STYLES_DIR, "cattrail.xml")
        self.stylexml_file_content = open(self.stylexml_file, "rb")
        self.zip3dfile = os.path.join(WAVEFRONT_DIR, "apple-tree.zip")
        self.zip3dfile_content = open(self.zip3dfile, "rb")

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestResourceCreateView(SetUpTest, TestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_create_geopackage(self):
        url = reverse('resource-create')
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name, self.thumbnail_content.read()
        )
        uploaded_gpkg = SimpleUploadedFile(
            self.gpkg_file_content.name, self.gpkg_file_content.read()
        )
        data = {
            "resource_type": "geopackage",
            "name": "Test Geopackage",
            "description": "A test geopackage",
            "thumbnail_full": uploaded_thumbnail,
            "file": uploaded_gpkg,
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Geopackage.objects.count(), 1)
        self.assertEqual(Geopackage.objects.first().name, "Test Geopackage")

    def test_create_layerdefinition(self):
        url = reverse('resource-create')
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name, self.thumbnail_content.read()
        )
        uploaded_qlr = SimpleUploadedFile(
            self.qlr_file_content.name, self.qlr_file_content.read()
        )
        data = {
            "resource_type": "layerdefinition",
            "name": "Test Layer Definition",
            "description": "A test layer definition",
            "thumbnail_full": uploaded_thumbnail,
            "file": uploaded_qlr,
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(LayerDefinition.objects.count(), 1)
        self.assertEqual(LayerDefinition.objects.first().name, "Test Layer Definition")

    def test_create_model(self):
        url = reverse('resource-create')
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name, self.thumbnail_content.read()
        )
        uploaded_model = SimpleUploadedFile(
            self.modelzip_file_content.name, self.modelzip_file_content.read()
        )
        data = {
            "resource_type": "model",
            "name": "Test Model",
            "description": "A test model",
            "thumbnail_full": uploaded_thumbnail,
            "file": uploaded_model,
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Model.objects.count(), 1)
        self.assertEqual(Model.objects.first().name, "Test Model")

    def test_create_style(self):
        url = reverse('resource-create')
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name, self.thumbnail_content.read()
        )
        uploaded_style = SimpleUploadedFile(
            self.stylexml_file_content.name, self.stylexml_file_content.read()
        )
        data = {
            "resource_type": "style",
            "name": "Test Style",
            "description": "A test style",
            "thumbnail_full": uploaded_thumbnail,
            "file": uploaded_style,
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Style.objects.count(), 1)
        self.assertEqual(Style.objects.first().name, "Test Style")

    def test_create_wavefront(self):
        url = reverse('resource-create')
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name, self.thumbnail_content.read()
        )
        uploaded_wavefront = SimpleUploadedFile(
            self.zip3dfile_content.name, self.zip3dfile_content.read()
        )
        data = {
            "resource_type": "3dmodel",
            "name": "Test 3D Model",
            "description": "A test 3D Model",
            "thumbnail_full": uploaded_thumbnail,
            "file": uploaded_wavefront,
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Wavefront.objects.count(), 1)
        self.assertEqual(Wavefront.objects.first().name, "Test 3D Model")

    def test_create_geopackage_invalid_data(self):
        url = reverse('resource-create')
        data = {
            "resource_type": "geopackage",
            "name": "",
            "description": "",
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Geopackage.objects.count(), 0)

    def test_create_style_invalid_data(self):
        url = reverse('resource-create')
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name, self.thumbnail_content.read()
        )
        uploaded_wavefront = SimpleUploadedFile(
            self.zip3dfile_content.name, self.zip3dfile_content.read()
        )
        data = {
            "resource_type": "style",
            "name": "Test Style",
            "description": "A test style",
            "thumbnail_full": uploaded_thumbnail,
            "file": uploaded_wavefront,
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Style.objects.count(), 0)

    def test_create_unsupported_resource_type(self):
        url = reverse('resource-create')
        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name, self.thumbnail_content.read()
        )
        uploaded_gpkg = SimpleUploadedFile(
            self.gpkg_file_content.name, self.gpkg_file_content.read()
        )
        data = {
            "resource_type": "unsupported",
            "name": "Test Unsupported",
            "description": "A test unsupported resource",
            "thumbnail_full": uploaded_thumbnail,
            "file": uploaded_gpkg,
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"resource_type": "Resource type not supported"})