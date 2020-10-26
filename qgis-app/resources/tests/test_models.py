import tempfile
from django.test import TestCase
from django.contrib.auth.models import User
from resources.models import Resource, ResourceType


class TestCRUD(TestCase):
    """
    Test Resource models
    """

    def setUp(self):
        """
        Sets up before each test
        """
        # https: // stackoverflow.com / a / 32814129 / 10268058
        self.image_temp = tempfile.NamedTemporaryFile(suffix=".png").name
        self.xml_temp = tempfile.NamedTemporaryFile(suffix=".xml").name
        self.marker_type = ResourceType.objects.create(name="marker",
                                 description="a marker for testing purpose",
                                 icon=self.image_temp)
        self.line_type = ResourceType.objects.create(name="line",
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
        self.resource_zero = Resource.objects.create(name="resource_zero",
            description="a resource for testing purpose",
            creator=self.user_staff,
            thumbnail_image=self.image_temp,
            xml_file=self.xml_temp)
        self.resource_zero.resource_types.add(self.marker_type)

    def test_create_resource_type(self):
        fill_type = ResourceType.objects.create(name="fill",
                                 description="a fill for testing purpose",
                                 icon=self.image_temp)
        self.assertEqual(fill_type.__str__(), "fill")

    def test_create_resource(self):
        resource_one = Resource.objects.create(name="resource_one",
                                description="a resource for testing purpose",
                                creator=self.user_staff,
                                thumbnail_image=self.image_temp,
                                xml_file=self.xml_temp)
        resource_one.resource_types.add(self.line_type)
        self.assertEqual(resource_one.name, "resource_one")
        self.assertEqual(resource_one.creator.first_name, "first_name_staff")
        self.assertEqual(resource_one.resource_types.first().name, "line")

    def test_update_resource(self):
        self.assertEqual(self.resource_zero.resource_types.count(), 1)
        self.resource_zero.resource_types.add(self.line_type)
        self.assertEqual(self.resource_zero.resource_types.count(), 2)
