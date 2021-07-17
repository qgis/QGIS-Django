"""Factories for building model instances for testing."""

import factory
import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile

from plugins.models import Plugin, PluginVersion, PluginInvalid


# TESTFILE_DIR = os.path.abspath(
#     os.path.join(os.path.dirname(__file__), 'testfiles'))
#
#
# ZIPFILE = InMemoryUploadedFile(
#             os.path.join(TESTFILE_DIR, "valid_metadata_link.zip"),
#             field_name='tempfile',
#             name='testfile.zip',
#             content_type='application/zip',
#             size=39889,
#             charset='utf8')

FAKE = factory.faker.faker.Faker()

class UserF(factory.django.DjangoModelFactory):
    """User model factory."""

    class Meta:
        model = User

    username = factory.Sequence(lambda n: "username%s" % n)
    first_name = FAKE.first_name()
    last_name = FAKE.last_name()
    email = FAKE.email()
    password = ''
    is_staff = False
    is_active = True
    is_superuser = False


class PluginF(factory.django.DjangoModelFactory):
    """Plugin model factory."""

    class Meta:
        model = Plugin

    created_by = factory.SubFactory(UserF)
    author = FAKE.name()
    email = FAKE.email()
    homepage = factory.Sequence(lambda n: "https://www.example-%s.com" % n)
    repository = "https://github.com/qgis/QGIS-Django"
    tracker = "https://github.com/qgis/QGIS-Django/issues"

    # name, desc etc.
    package_name = factory.Sequence(lambda n: "package_%s" % n)
    name = factory.Sequence(lambda n: "name_%s" % n)
    description = factory.Sequence(lambda n: "Description of name_%s" % n)
    about = factory.Sequence(lambda n: "About name_%s" % n)

    # downloads (soft trigger from versions)
    downloads = factory.Sequence(lambda n: n)


class PluginVersionF(factory.django.DjangoModelFactory):
    """PluginVersion model factory."""

    class Meta:
        model = PluginVersion

    # link to parent
    plugin = factory.SubFactory(PluginF)
    created_by = factory.SubFactory(UserF)
    min_qg_version = "002.000.000"
    max_qg_version = "002.099.003.###"
    version = "1.2.3.4"
    package = factory.django.FileField(filename='plugin.zip')


class PluginInvalidF(factory.django.DjangoModelFactory):
    """PluginVersion model factory."""

    class Meta:
        model = PluginInvalid

    plugin = factory.SubFactory(PluginF)
    validated_version = "0.0.0.0"
    message = "File does not exist. Please re-upload."
