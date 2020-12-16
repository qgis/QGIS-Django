import os

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from base.models.models_sharing_file import Resource, Review

MODELERS_STORAGE_PATH = getattr(settings,
                                 'MODELERS_STORAGE_PATH', 'modelers/%Y')


class Modeler(Resource):
    """
    Modeler Model.

    """

    # thumbnail
    thumbnail_image = models.ImageField(
        _('Thumbnail'),
        help_text=_('Please upload an image that demonstrate this Model'),
        blank=False,
        null=False,
        upload_to=MODELERS_STORAGE_PATH)

    # file
    model_file = models.FileField(
        _('Model file'),
        help_text=_('A Model file. The filesize must less than 1MB '),
        upload_to=MODELERS_STORAGE_PATH,
        validators=[FileExtensionValidator(
            allowed_extensions=['model3', 'zip'])],
        null=False)

    def extension(self):
        name, extension = os.path.splitext(self.model_file.name)
        return extension

    def get_absolute_url(self):
        return reverse('modeler_detail', args=(self.id,))


class ModelerReview(Review):
    """
    A Modeler Review Model.
    """

    # modeler
    modeler = models.ForeignKey(Modeler,
                                verbose_name=_('Model'),
                                help_text=_('The reviewed Model'),
                                blank=False,
                                null=False,
                                on_delete=models.CASCADE)
