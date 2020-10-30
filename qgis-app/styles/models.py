from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

STYLES_STORAGE_PATH = getattr(settings,
                                 'PLUGINS_STORAGE_PATH', 'styles/%Y')


class StyleType(models.Model):
    """
    Style Type model
    """

    # symbol, name and desc
    # symbol_type e.g. "line"
    # name e.g. "Line"
    symbol_type = models.CharField(
        _('Symbol type'),
        help_text=_('This Symbol will be used to identify the type of a style '
                    'based on an attribute value in the uploaded XML file.'),
        max_length=256,
        unique=True)
    name = models.CharField(
        _('Name'),
        help_text=_('An unique name of this style type.'),
        max_length=256,
        unique=True)
    description = models.TextField(
        _('Description'),
        help_text=_('A short description of this style type.'),
        max_length=1000,
        blank=True,
        null=True)

    # icon image
    icon = models.ImageField(
        _('Icon'),
        help_text=_('An icon for this style type.'),
        upload_to=STYLES_STORAGE_PATH)

    # ordering for Style instance
    order = models.IntegerField(
        _('Order'),
        help_text=_('Order value for custom ordering.'),
        default=0)

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return "%s" % (self.name)

    def __str__(self):
        return self.__unicode__()


class Style(models.Model):
    """
    Style model
    """

    # date
    upload_date = models.DateTimeField(
        _('Uploaded on'),
        help_text=_('The upload date.'),
        auto_now_add=True,
        editable=False)

    # creator
    creator = models.ForeignKey(
        User,
        verbose_name=_('Created by'),
        help_text=_('The user who upload this style.'),
        related_name='styles_created_by',
        on_delete=models.CASCADE)

    # style type
    style_type = models.ForeignKey(StyleType,
        verbose_name=_('Type'),
        help_text=_('The type of this style.'),
        blank=True,
        null=True,
        on_delete=models.CASCADE)

    # name and desc
    name = models.CharField(_('Name'),
        help_text=_('An unique name for this style'),
        max_length=256,
        unique=True)
    description = models.TextField(
        _('Description'),
        help_text=_('A description of this style.'),
        max_length=5000
    )

    # thumbnail
    thumbnail_image = models.ImageField(
        _('Thumbnail'),
        help_text=_('Please upload an image that represent this style.'),
        blank=True,
        null=True,
        upload_to=STYLES_STORAGE_PATH)

    # file
    xml_file = models.FileField(
        _('Style file'),
        help_text=_('A style file in XML format'),
        upload_to=STYLES_STORAGE_PATH,
        validators=[FileExtensionValidator(allowed_extensions=['xml'])],
        null=False)

    # counter
    download_count = models.IntegerField(
        _('Downloads'),
        help_text=_('The number of times this style has been downloaded.'),
        default=0,
        editable=False)

    def __unicode__(self):
        return "%s" % (self.name)

    def __str__(self):
        return self.__unicode__()
