import os

from base.models.processing_models import Resource, ResourceReview
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

GEOPACKAGES_STORAGE_PATH = getattr(
    settings, "GEOPACKAGE_STORAGE_PATH", "geopackages/%Y"
)


class Geopackage(Resource):

    # file
    file = models.FileField(
        _("GeoPackage file"),
        help_text=_("A GeoPackage file. The filesize must less than 1MB "),
        upload_to=GEOPACKAGES_STORAGE_PATH,
        validators=[FileExtensionValidator(allowed_extensions=["gpkg", "zip"])],
        null=False,
    )

    # thumbnail
    thumbnail_image = models.ImageField(
        _("Thumbnail"),
        help_text=_("Please upload an image that demonstrate this resource."),
        blank=False,
        null=False,
        upload_to=GEOPACKAGES_STORAGE_PATH,
    )

    def get_absolute_url(self):
        return reverse("geopackage_detail", args=(self.id,))

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension


class Review(ResourceReview):

    # Geopackage resource
    resource = models.ForeignKey(
        Geopackage,
        verbose_name=_("GeoPackage"),
        help_text=_("The reviewed GeoPackage"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
