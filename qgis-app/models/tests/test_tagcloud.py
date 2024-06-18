from django.test import TestCase, RequestFactory, override_settings
from taggit.models import Tag
from models.templatetags import resources_tagcloud
from models.models import Model
from models.tests.test_views import SetUpTest
from django.template import Context, Template
import tempfile

@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TagCloudTests(SetUpTest, TestCase):
    fixtures = ["fixtures/simplemenu.json"]

    def setUp(self):
        super(TagCloudTests, self).setUp()

        self.tag1 = Tag.objects.create(name='model')
        self.tag2 = Tag.objects.create(name='project')

        self.model_instance = Model.objects.create(
            creator=self.creator,
            name="flooded buildings extractor",
            description="A Model for testing purpose",
            thumbnail_image=self.thumbnail,
            file=self.file,
            approved=True
        )
        self.model_instance.tags.add(self.tag1, self.tag2)

        self.factory = RequestFactory()

    def test_get_queryset(self):
        queryset = resources_tagcloud.get_queryset('models', 'model')
        self.assertEqual(list(queryset), [self.tag1, self.tag2])

    def test_get_resources_tagcloud(self):
        context = Context({'request': self.factory.get('/')})
        tags = resources_tagcloud.get_resources_tagcloud(context, 'models', 'model')
        self.assertIn(self.tag1, tags)
        self.assertIn(self.tag2, tags)
        self.assertTrue(hasattr(tags.first(), 'weight'))

    def test_include_resources_tagcloud_modal(self):
        context = Context({'request': self.factory.get('/')})
        rendered = Template(
            '{% load resources_tagcloud %}{% include_resources_tagcloud_modal "models" "model" %}'
        ).render(context)

        self.assertIn('model', rendered)
        self.assertIn('project', rendered)
        self.assertIn('Model Tags', rendered)
