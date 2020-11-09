import tempfile

from django.test import SimpleTestCase, TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from styles.models import Style, StyleType

from styles.views import StyleListView, style_download


class TestURL(TestCase):
    def test_url(self):
        url = reverse('style_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TestDownload(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_staff = User.objects.create(username='usertest_staff',
                                              first_name="first_name_staff",
                                              last_name="last_name_staff",
                                              email="staff@example.com",
                                              password="passwordtest",
                                              is_active=True,
                                              is_staff=True,
                                              is_superuser=False)
        self.image_temp = tempfile.NamedTemporaryFile(suffix=".png").name
        self.xml_temp = tempfile.NamedTemporaryFile(suffix=".xml").name
        self.marker_type = StyleType.objects.create(symbol_type="marker",
                                                    name="Marker",
                                                    description="a marker for testing purpose",
                                                    icon=self.image_temp)
        self.style_zero = Style.objects.create(name="style_zero",
                                               description="a style for testing purpose",
                                               creator=self.user_staff,
                                               thumbnail_image=self.image_temp,
                                               xml_file=self.xml_temp,
                                               style_type=self.marker_type)

    def test_object_detail(self):
        style_zero = Style.objects.filter(name="style_zero").first()
        url = reverse('style_detail', kwargs={'pk': style_zero.id})
        request = self.factory.get(url)
        response = StyleListView.as_view()(request)
        self.assertEqual(response.status_code, 200)
