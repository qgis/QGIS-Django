import os

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from base.models.processing_models import Resource, ResourceReview

LAYERDEFINITIONS_STORAGE_PATH = getattr(
    settings, 'LAYERDEFINITION_STORAGE_PATH', 'layerdefinitions')


class LayerDefinition(Resource):
    """QGIS Layer Definition File (.qlr) Model."""

    # file
    file = models.FileField(
        _('Layer Definition file'),
        help_text=_('A Layer Definition file. '
                    'The filesize must less than 1MB'),
        upload_to=LAYERDEFINITIONS_STORAGE_PATH,
        validators=[FileExtensionValidator(allowed_extensions=['qlr'])],
        null=False)

    # thumbnail
    thumbnail_image = models.ImageField(
        _('Thumbnail'),
        help_text=_('Please upload an image that demonstrate this resource.'),
        blank=False,
        null=False,
        upload_to=LAYERDEFINITIONS_STORAGE_PATH)

    # url datasource
    url_datasource = models.URLField(
        _('URL Data Source.'),
        blank=True,
        null=True,
        max_length=200)

    # url metadata
    url_metadata = models.URLField(
        _('URL Metadata'),
        help_text=_('Please add a URL where we can find metadata information '
                    'of this resource.'),
        blank=True,
        null=True,
        max_length=200)

    # provider
    provider = models.TextField(
        _('Provider'),
        max_length=100,
        blank=True,
        null=True
    )

    # license
    license = models.TextField(
        _('License'),
        help_text=_('License of this resource.'),
        max_length=500,
        blank=True,
        null=True
    )

    def get_absolute_url(self):
        return reverse('layerdefinition_detail', args=(self.id,))

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension


class Review(ResourceReview):

    # Layer Definition resource
    resource = models.ForeignKey(
        LayerDefinition,
        verbose_name=_('Layer Definition'),
        help_text=_('The reviewed Layer Definition.'),
        blank=False,
        null=False,
        on_delete=models.CASCADE)
