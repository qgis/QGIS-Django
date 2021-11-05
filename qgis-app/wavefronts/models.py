import os

from preferences.models import Preferences

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from base.models.processing_models import Resource, ResourceReview

WAVEFRONTS_STORAGE_PATH = getattr(
    settings, 'WAVEFRONTS_STORAGE_PATH', 'wavefronts')


class Wavefront(Resource):
    """
    Wavefront Model.

    """

    # thumbnail
    thumbnail_image = models.ImageField(
        _('Thumbnail'),
        help_text=_('Please upload an image that demonstrate this Wavefront'),
        blank=False,
        null=False,
        upload_to=WAVEFRONTS_STORAGE_PATH)

    # file
    file = models.FileField(
        _('Wavefront file'),
        help_text=_('A Wavefront file. The filesize must less than 1MB '),
        upload_to=WAVEFRONTS_STORAGE_PATH,
        validators=[FileExtensionValidator(
            allowed_extensions=['model3', 'zip'])],
        null=False)

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension

    def get_absolute_url(self):
        return reverse('wavefront_detail', args=(self.id,))


class Review(ResourceReview):
    """
    A Wavefront Review Model.
    """

    # Model resource
    resource = models.ForeignKey(
        Wavefront,
        verbose_name=_('Wavefront'),
        help_text=_('The reviewed Wavefront'),
        blank=False,
        null=False,
        on_delete=models.CASCADE
    )


class FilesizePreferences(Preferences):
    __module__ = 'preferences.models'
    wavefront_filesize_limit = models.FloatField(
        help_text=_('filesize in mb'),
        default=10
    )
