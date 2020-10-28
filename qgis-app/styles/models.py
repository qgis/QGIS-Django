from django.db import models

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
    # symbol e.g. "line"
    # name e.g. "Line"
    symbol = models.CharField(_('Symbol'),
                            help_text=_('Must be unique'),
                            max_length=256,
                            unique=True)
    name = models.CharField(_('Name'),
                            help_text=_('Must be unique'),
                            max_length=256,
                            unique=True)
    description = models.TextField(_('Description'))

    # icon image
    icon = models.ImageField(_('Icon'),
                             upload_to=STYLES_STORAGE_PATH)

    # ordering for Style instance
    order = models.IntegerField(_('Order'),
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
    upload_date = models.DateTimeField(_('Uploaded on'),
                                       auto_now_add=True,
                                       editable=False)

    # creator
    creator = models.ForeignKey(User, verbose_name=_('Created by'),
                                related_name='styles_created_by',
                                on_delete=models.CASCADE)

    # style type
    style_type = models.ForeignKey(StyleType,
                                      verbose_name=_('Type'),
                                      blank=True,
                                      null=True,
                                      on_delete=models.CASCADE)

    # name and desc
    name = models.CharField(_('Name'),
                            help_text=_('Must be unique'),
                            max_length=256,
                            unique=True)
    description = models.TextField(_('Description'))

    # thumbnail
    thumbnail_image = models.ImageField(_('Thumbnail'), blank=True,
                             null=True, upload_to=STYLES_STORAGE_PATH)

    # file
    xml_file = models.FileField(_('Style file'),
                                upload_to=STYLES_STORAGE_PATH,
                                null=False)

    # counter
    download_count = models.IntegerField(_('Downloads'),
                                         default=0,
                                         editable=False)

    def __unicode__(self):
        return "%s" % (self.name)

    def __str__(self):
        return self.__unicode__()
