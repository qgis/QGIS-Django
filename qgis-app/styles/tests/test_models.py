import tempfile
from django.test import TestCase
from django.contrib.auth.models import User
from styles.models import Style, StyleType


class TestCRUD(TestCase):
    """
    Test Styles models
    """

    def setUp(self):
        """
        Sets up before each test
        """
        # https://stackoverflow.com/a/32814129/10268058
        self.image_temp = tempfile.NamedTemporaryFile(suffix=".png").name
        self.xml_temp = tempfile.NamedTemporaryFile(suffix=".xml").name
        self.marker_type = StyleType.objects.create(symbol_type="marker",
                                 name="Marker",
                                 description="a marker for testing purpose",
                                 icon=self.image_temp)
        self.line_type = StyleType.objects.create(symbol_type="line",
                                 name="Line",
                                 description="a line for testing purpose",
                                 icon=self.image_temp)
        self.user_staff = User.objects.create(username='usertest_staff',
                                        first_name="first_name_staff",
                                        last_name="last_name_staff",
                                        email="staff@example.com",
                                        password="passwordtest",
                                        is_active=True,
                                        is_staff=True,
                                        is_superuser=False)
        self.style_zero = Style.objects.create(name="style_zero",
            description="a style for testing purpose",
            creator=self.user_staff,
            thumbnail_image=self.image_temp,
            file=self.xml_temp,
            style_type=self.marker_type)

    def test_create_style_type(self):
        fill_type = StyleType.objects.create(symbol_type="fill",
                                 name="Fill",
                                 description="a fill for testing purpose",
                                 icon=self.image_temp)
        self.assertEqual(fill_type.__str__(), "Fill")

    def test_create_style(self):
        style_one = Style.objects.create(name="style_one",
                                description="a style for testing purpose",
                                creator=self.user_staff,
                                thumbnail_image=self.image_temp,
                                file=self.xml_temp,
                                style_type=self.line_type)
        self.assertEqual(style_one.name, "style_one")
        self.assertEqual(style_one.creator.first_name, "first_name_staff")
        self.assertEqual(style_one.style_type.name, "Line")

    def test_update_style(self):
        self.assertEqual(self.style_zero.style_type.name, "Marker")
        self.style_zero.style_type = self.line_type
        self.assertEqual(self.style_zero.style_type.name, "Line")
