import os

from base.models.processing_models import Resource, ResourceReview
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

MODELS_STORAGE_PATH = getattr(settings, "MODELS_STORAGE_PATH", "models/%Y")


class Model(Resource):
    """
    Model Model.

    """

    # thumbnail
    thumbnail_image = models.ImageField(
        _("Thumbnail"),
        help_text=_("Please upload an image that demonstrate this Model"),
        blank=False,
        null=False,
        upload_to=MODELS_STORAGE_PATH,
    )

    # file
    file = models.FileField(
        _("Model file"),
        help_text=_("A Model file. The filesize must less than 1MB "),
        upload_to=MODELS_STORAGE_PATH,
        validators=[FileExtensionValidator(allowed_extensions=["model3", "zip"])],
        null=False,
    )

    def extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension

    def get_absolute_url(self):
        return reverse("model_detail", args=(self.id,))


class Review(ResourceReview):
    """
    A Model Review Model.
    """

    # Model resource
    resource = models.ForeignKey(
        Model,
        verbose_name=_("Model"),
        help_text=_("The reviewed Model"),
        blank=False,
        null=False,
        on_delete=models.CASCADE,
    )
