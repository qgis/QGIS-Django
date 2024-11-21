
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

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from api.models import UserOutstandingToken

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
        self.client.login(username='testuser', password='testpass')
        self.refresh = RefreshToken.for_user(self.user)
        self.outstanding_token = OutstandingToken.objects.get(jti=self.refresh['jti'])
        self.user_token = UserOutstandingToken.objects.create(
            user=self.user,
            token=self.outstanding_token,
            is_blacklisted=False,
            is_newly_created=True
        )
        self.url = reverse('user_token_detail', args=[self.user_token.pk])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        access_token = response.context.get('access_token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

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

    def test_create_with_invalid_token(self):
        url = reverse('resource-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
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
        self.assertEqual(response.status_code, 401)

    def test_create_with_blacklisted_token(self):
        url = reverse('resource-create')
        self.refresh.blacklist()
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
        self.assertEqual(response.status_code, 403)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestResourceDetailView(SetUpTest, TestCase):

    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.refresh = RefreshToken.for_user(self.user)
        self.outstanding_token = OutstandingToken.objects.get(jti=self.refresh['jti'])
        self.user_token = UserOutstandingToken.objects.create(
            user=self.user,
            token=self.outstanding_token,
            is_blacklisted=False,
            is_newly_created=True
        )
        self.url = reverse('user_token_detail', args=[self.user_token.pk])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        access_token = response.context.get('access_token')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        uploaded_thumbnail = SimpleUploadedFile(
            self.thumbnail_content.name, self.thumbnail_content.read()
        )
        uploaded_gpkg = SimpleUploadedFile(
            self.gpkg_file_content.name, self.gpkg_file_content.read()
        )
        uploaded_qlr = SimpleUploadedFile(
            self.qlr_file_content.name, self.qlr_file_content.read()
        )
        uploaded_model = SimpleUploadedFile(
            self.modelzip_file_content.name, self.modelzip_file_content.read()
        )
        uploaded_style = SimpleUploadedFile(
            self.stylexml_file_content.name, self.stylexml_file_content.read()
        )
        uploaded_wavefront = SimpleUploadedFile(
            self.zip3dfile_content.name, self.zip3dfile_content.read()
        )

        self.geopackage = Geopackage.objects.create(
            creator=self.user,
            name="Test Geopackage",
            description="A test geopackage",
            thumbnail_image=uploaded_thumbnail,
            file=uploaded_gpkg,
        )
        self.geopackage.approved = True
        self.geopackage.save()

        self.layerdefinition = LayerDefinition.objects.create(
            creator=self.user,
            name="Test Layer Definition",
            description="A test layer definition",
            thumbnail_image=uploaded_thumbnail,
            file=uploaded_qlr,
        )
        self.layerdefinition.approved = True
        self.layerdefinition.save()

        self.model = Model.objects.create(
            creator=self.user,
            name="Test Model",
            description="A test model",
            thumbnail_image=uploaded_thumbnail,
            file=uploaded_model,
        )
        self.model.approved = True
        self.model.save()

        self.style = Style.objects.create(
            creator=self.user,
            name="Test Style",
            description="A test style",
            thumbnail_image=uploaded_thumbnail,
            file=uploaded_style,
        )
        self.style.approved = True
        self.style.save()

        self.wavefront = Wavefront.objects.create(
            creator=self.user,
            name="Test 3D Model",
            description="A test 3D model",
            thumbnail_image=uploaded_thumbnail,
            file=uploaded_wavefront,
        )
        self.wavefront.approved = True
        self.wavefront.save()


    def test_get_geopackage(self):
        url = reverse("resource-detail", kwargs={"uuid": self.geopackage.uuid, "resource_type": "geopackage"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test Geopackage")

    def test_get_layerdefinition(self):
        url = reverse("resource-detail", kwargs={"uuid": self.layerdefinition.uuid, "resource_type": "layerdefinition"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test Layer Definition")

    def test_get_model(self):
        url = reverse("resource-detail", kwargs={"uuid": self.model.uuid, "resource_type": "model"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test Model")

    def test_get_style(self):
        url = reverse("resource-detail", kwargs={"uuid": self.style.uuid, "resource_type": "style"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test Style")

    def test_get_wavefront(self):
        url = reverse("resource-detail", kwargs={"uuid": self.wavefront.uuid, "resource_type": "3dmodel"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["name"], "Test 3D Model")

    def test_update_geopackage(self):
        url = reverse("resource-detail", kwargs={"uuid": self.geopackage.uuid, "resource_type": "geopackage"})
        data = {
            "name": "Updated Geopackage",
            "description": "Updated description",
            "thumbnail_full": self.geopackage.thumbnail_image,
            "file": self.geopackage.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.geopackage.refresh_from_db()
        self.assertEqual(self.geopackage.name, "Updated Geopackage")

    def test_update_layerdefinition(self):
        url = reverse("resource-detail", kwargs={"uuid": self.layerdefinition.uuid, "resource_type": "layerdefinition"})
        data = {
            "name": "Updated Layer Definition",
            "description": "Updated description",
            "thumbnail_full": self.layerdefinition.thumbnail_image,
            "file": self.layerdefinition.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.layerdefinition.refresh_from_db()
        self.assertEqual(self.layerdefinition.name, "Updated Layer Definition")

    def test_update_model(self):
        url = reverse("resource-detail", kwargs={"uuid": self.model.uuid, "resource_type": "model"})
        data = {
            "name": "Updated Model",
            "description": "Updated description",
            "thumbnail_full": self.model.thumbnail_image,
            "file": self.model.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.model.refresh_from_db()
        self.assertEqual(self.model.name, "Updated Model")

    def test_update_style(self):
        url = reverse("resource-detail", kwargs={"uuid": self.style.uuid, "resource_type": "style"})
        data = {
            "name": "Updated Style",
            "description": "Updated description",
            "thumbnail_full": self.style.thumbnail_image,
            "file": self.style.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.style.refresh_from_db()
        self.assertEqual(self.style.name, "Updated Style")

    def test_update_wavefront(self):
        url = reverse("resource-detail", kwargs={"uuid": self.wavefront.uuid, "resource_type": "3dmodel"})
        data = {
            "name": "Updated 3D Model",
            "description": "Updated description",
            "thumbnail_full": self.wavefront.thumbnail_image,
            "file": self.wavefront.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.wavefront.refresh_from_db()
        self.assertEqual(self.wavefront.name, "Updated 3D Model")

    def test_delete_geopackage(self):
        url = reverse("resource-detail", kwargs={"uuid": self.geopackage.uuid, "resource_type": "geopackage"})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Geopackage.objects.filter(uuid=self.geopackage.uuid).exists())

    def test_delete_layerdefinition(self):
        url = reverse("resource-detail", kwargs={"uuid": self.layerdefinition.uuid, "resource_type": "layerdefinition"})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(LayerDefinition.objects.filter(uuid=self.layerdefinition.uuid).exists())

    def test_delete_model(self):
        url = reverse("resource-detail", kwargs={"uuid": self.model.uuid, "resource_type": "model"})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Model.objects.filter(uuid=self.model.uuid).exists())

    def test_delete_style(self):
        url = reverse("resource-detail", kwargs={"uuid": self.style.uuid, "resource_type": "style"})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Style.objects.filter(uuid=self.style.uuid).exists())

    def test_delete_wavefront(self):
        url = reverse("resource-detail", kwargs={"uuid": self.wavefront.uuid, "resource_type": "3dmodel"})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Wavefront.objects.filter(uuid=self.wavefront.uuid).exists())

    def test_update_geopackage_with_invalid_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.geopackage.uuid, "resource_type": "geopackage"})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        data = {
            "name": "Updated Geopackage",
            "description": "Updated description",
            "thumbnail_full": self.geopackage.thumbnail_image,
            "file": self.geopackage.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 401)

    def test_update_geopackage_with_blacklisted_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.geopackage.uuid, "resource_type": "geopackage"})
        self.refresh.blacklist()
        data = {
            "name": "Updated Geopackage",
            "description": "Updated description",
            "thumbnail_full": self.geopackage.thumbnail_image,
            "file": self.geopackage.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 403)

    def test_update_layerdefinition_with_invalid_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.layerdefinition.uuid, "resource_type": "layerdefinition"})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        data = {
            "name": "Updated Layer Definition",
            "description": "Updated description",
            "thumbnail_full": self.layerdefinition.thumbnail_image,
            "file": self.layerdefinition.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 401)

    def test_update_layerdefinition_with_blacklisted_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.layerdefinition.uuid, "resource_type": "layerdefinition"})
        self.refresh.blacklist()
        data = {
            "name": "Updated Layer Definition",
            "description": "Updated description",
            "thumbnail_full": self.layerdefinition.thumbnail_image,
            "file": self.layerdefinition.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 403)

    def test_update_model_with_invalid_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.model.uuid, "resource_type": "model"})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        data = {
            "name": "Updated Model",
            "description": "Updated description",
            "thumbnail_full": self.model.thumbnail_image,
            "file": self.model.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 401)

    def test_update_model_with_blacklisted_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.model.uuid, "resource_type": "model"})
        self.refresh.blacklist()
        data = {
            "name": "Updated Model",
            "description": "Updated description",
            "thumbnail_full": self.model.thumbnail_image,
            "file": self.model.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 403)

    def test_update_style_with_invalid_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.style.uuid, "resource_type": "style"})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        data = {
            "name": "Updated Style",
            "description": "Updated description",
            "thumbnail_full": self.style.thumbnail_image,
            "file": self.style.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 401)

    def test_update_style_with_blacklisted_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.style.uuid, "resource_type": "style"})
        self.refresh.blacklist()
        data = {
            "name": "Updated Style",
            "description": "Updated description",
            "thumbnail_full": self.style.thumbnail_image,
            "file": self.style.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 403)

    def test_update_wavefront_with_invalid_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.wavefront.uuid, "resource_type": "3dmodel"})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        data = {
            "name": "Updated 3D Model",
            "description": "Updated description",
            "thumbnail_full": self.wavefront.thumbnail_image,
            "file": self.wavefront.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 401)

    def test_update_wavefront_with_blacklisted_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.wavefront.uuid, "resource_type": "3dmodel"})
        self.refresh.blacklist()
        data = {
            "name": "Updated 3D Model",
            "description": "Updated description",
            "thumbnail_full": self.wavefront.thumbnail_image,
            "file": self.wavefront.file,
        }
        response = self.client.put(url, data, format="multipart")
        self.assertEqual(response.status_code, 403)

    def test_delete_geopackage_with_invalid_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.geopackage.uuid, "resource_type": "geopackage"})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)
        self.assertTrue(Geopackage.objects.filter(uuid=self.geopackage.uuid).exists())

    def test_delete_geopackage_with_blacklisted_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.geopackage.uuid, "resource_type": "geopackage"})
        self.refresh.blacklist()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Geopackage.objects.filter(uuid=self.geopackage.uuid).exists())

    def test_delete_layerdefinition_with_invalid_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.layerdefinition.uuid, "resource_type": "layerdefinition"})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)
        self.assertTrue(LayerDefinition.objects.filter(uuid=self.layerdefinition.uuid).exists())

    def test_delete_layerdefinition_with_blacklisted_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.layerdefinition.uuid, "resource_type": "layerdefinition"})
        self.refresh.blacklist()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(LayerDefinition.objects.filter(uuid=self.layerdefinition.uuid).exists())

    def test_delete_model_with_invalid_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.model.uuid, "resource_type": "model"})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)
        self.assertTrue(Model.objects.filter(uuid=self.model.uuid).exists())

    def test_delete_model_with_blacklisted_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.model.uuid, "resource_type": "model"})
        self.refresh.blacklist()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Model.objects.filter(uuid=self.model.uuid).exists())

    def test_delete_style_with_invalid_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.style.uuid, "resource_type": "style"})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)
        self.assertTrue(Style.objects.filter(uuid=self.style.uuid).exists())

    def test_delete_style_with_blacklisted_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.style.uuid, "resource_type": "style"})
        self.refresh.blacklist()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Style.objects.filter(uuid=self.style.uuid).exists())

    def test_delete_wavefront_with_invalid_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.wavefront.uuid, "resource_type": "3dmodel"})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)
        self.assertTrue(Wavefront.objects.filter(uuid=self.wavefront.uuid).exists())

    def test_delete_wavefront_with_blacklisted_token(self):
        url = reverse("resource-detail", kwargs={"uuid": self.wavefront.uuid, "resource_type": "3dmodel"})
        self.refresh.blacklist()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Wavefront.objects.filter(uuid=self.wavefront.uuid).exists())