import json

from django.contrib.auth.models import User, Group
from django.core.files.base import ContentFile
from django.test import TestCase, Client
from django.urls import reverse

# models
from geopackages.models import Geopackage
from models.models import Model
from styles.models import Style, StyleType

from django.core.files.uploadedfile import SimpleUploadedFile


class TestResourceAPIList(TestCase):
    def setUp(self):
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        self.thumbnail = SimpleUploadedFile(
            'small.gif', small_gif, content_type='image/gif')
        self.file = ContentFile('text', 'filename')

        self.creator = User.objects.create(
            username="creator", email="creator@email.com"
        )
        self.creator0 = User.objects.create(
            username="creator 0", email="creator0@email.com"
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
        style_type = StyleType.objects.create(
            symbol_type="marker",
            name="Marker",
            description="a marker for testing purpose",
            icon=self.thumbnail)
        Style.objects.create(
            name="style_zero",
            description="a style for testing purpose",
            creator=self.creator,
            thumbnail_image=self.thumbnail,
            file=self.file,
            style_type=style_type,
            approved=True
        )
        # create geopackage
        Geopackage.objects.create(
            creator=self.creator,
            name="spiky polygons",
            description="A GeoPackage for testing purpose",
            thumbnail_image=self.thumbnail,
            file=self.file,
            approved=True
        )
        #create Model
        Model.objects.create(
            creator=self.creator0,
            name="flooded buildings extractor",
            description="A Model for testing purpose",
            thumbnail_image=self.thumbnail,
            file=self.file,
            approved=True
        )

    def tearDown(self):
        pass

    def test_get_list_resources(self):
        """ test results all resources """
        url = reverse('resource-list')
        response = self.client.get(url)
        json_parse = json.loads(response.content)
        self.assertEqual(json_parse['overall_total'], 3)
        result = json_parse['results']
        for i, d in enumerate(result):
            if d['type'] == 'geopackage':
                g_index = i
            elif d['type'] == 'model':
                m_index = i
            elif d['type'] == 'style':
                s_index = i
        self.assertIsNotNone(g_index)
        self.assertIsNotNone(m_index)
        self.assertIsNotNone(s_index)
        self.assertEqual(result[g_index]['resource_type'], 'Geopackage')
        self.assertEqual(result[g_index]['resource_subtype'], None)
        self.assertEqual(result[g_index]['creator'], 'creator')
        self.assertEqual(result[m_index]['resource_type'], 'Model')
        self.assertEqual(result[m_index]['resource_subtype'], None)
        self.assertEqual(result[m_index]['creator'], 'creator 0')
        self.assertEqual(result[s_index]['resource_type'], 'Style')
        self.assertEqual(result[s_index]['resource_subtype'], 'Marker')
        self.assertEqual(result[s_index]['creator'], 'creator')

    def test_get_list_resources_with_filter(self):
        param = ('resource_type=geopackage')
        url = '%s?%s' % (reverse('resource-list'), param)
        response = self.client.get(url)
        json_parse = json.loads(response.content)
        self.assertEqual(json_parse['overall_total'], 1)
        result = json_parse['results']
        g_index = None
        m_index = None
        s_index = None
        for i, d in enumerate(result):
            if d['type'] == 'geopackage':
                g_index = i
            elif d['type'] == 'model':
                m_index = i
            elif d['type'] == 'style':
                s_index = i
        self.assertIsNotNone(g_index)
        self.assertIsNone(m_index)
        self.assertIsNone(s_index)

    def test_get_list_resources_with_filter_resource_type(self):
        param = ('resource_type=geopackage')
        url = '%s?%s' % (reverse('resource-list'), param)
        response = self.client.get(url)
        json_parse = json.loads(response.content)
        self.assertEqual(json_parse['overall_total'], 1)
        result = json_parse['results']
        g_index = None
        m_index = None
        s_index = None
        for i, d in enumerate(result):
            if d['type'] == 'geopackage':
                g_index = i
            elif d['type'] == 'model':
                m_index = i
            elif d['type'] == 'style':
                s_index = i
        self.assertIsNotNone(g_index)
        self.assertIsNone(m_index)
        self.assertIsNone(s_index)

    def test_get_list_resources_with_filter_resource_type(self):
        param = ('resource_subtype=Marker')
        url = '%s?%s' % (reverse('resource-list'), param)
        response = self.client.get(url)
        json_parse = json.loads(response.content)
        self.assertEqual(json_parse['overall_total'], 1)
        result = json_parse['results']
        g_index = None
        m_index = None
        s_index = None
        for i, d in enumerate(result):
            if d['type'] == 'geopackage':
                g_index = i
            elif d['type'] == 'model':
                m_index = i
            elif d['type'] == 'style':
                s_index = i
        self.assertIsNone(g_index)
        self.assertIsNone(m_index)
        self.assertIsNotNone(s_index)

    def test_get_list_resources_with_filter_creator(self):
        param = ('creator=creator 0')
        url = '%s?%s' % (reverse('resource-list'), param)
        response = self.client.get(url)
        json_parse = json.loads(response.content)
        self.assertEqual(json_parse['overall_total'], 1)
        result = json_parse['results']
        g_index = None
        m_index = None
        s_index = None
        for i, d in enumerate(result):
            if d['type'] == 'geopackage':
                g_index = i
            elif d['type'] == 'model':
                m_index = i
            elif d['type'] == 'style':
                s_index = i
        self.assertIsNone(g_index)
        self.assertIsNotNone(m_index)
        self.assertIsNone(s_index)

    def test_get_list_resources_with_filter_keyword(self):
        param = ('keyword=testing')
        url = '%s?%s' % (reverse('resource-list'), param)
        response = self.client.get(url)
        json_parse = json.loads(response.content)
        self.assertEqual(json_parse['overall_total'], 3)
        result = json_parse['results']
        g_index = None
        m_index = None
        s_index = None
        for i, d in enumerate(result):
            if d['type'] == 'geopackage':
                g_index = i
            elif d['type'] == 'model':
                m_index = i
            elif d['type'] == 'style':
                s_index = i
        self.assertIsNotNone(g_index)
        self.assertIsNotNone(m_index)
        self.assertIsNotNone(s_index)
