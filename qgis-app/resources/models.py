from django.db import models

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

RESOURCES_STORAGE_PATH = getattr(settings,
                                 'PLUGINS_STORAGE_PATH', 'resources/%Y')


class ResourceType(models.Model):
    """
    ResourceType model
    """

    # name and desc
    name = models.CharField(_('Name'),
                            help_text=_('Must be unique'),
                            max_length=256,
                            unique=True)
    description = models.TextField(_('Description'))

    # icon image
    icon = models.ImageField(_('Icon'),
                             upload_to=RESOURCES_STORAGE_PATH)

    # ordering for Resource instance
    order = models.IntegerField(_('Order'),
                                default=0)

    class Meta:
        ordering = ('order',)

    def __unicode__(self):
        return "%s" % (self.name)

    def __str__(self):
        return self.__unicode__()


class Resource(models.Model):
    """
    Resource model
    """

    # date
    upload_date = models.DateTimeField(_('Uploaded on'),
                                       auto_now_add=True,
                                       editable=False)

    # creator
    creator = models.ForeignKey(User, verbose_name=_('Created by'),
                                related_name='resources_created_by',
                                on_delete=models.CASCADE)

    # resource type
    resource_types = models.ManyToManyField(ResourceType,
                                      verbose_name=_('Type'),
                                      blank=True)

    # name and desc
    name = models.CharField(_('Name'),
                            help_text=_('Must be unique'),
                            max_length=256,
                            unique=True)
    description = models.TextField(_('Description'))

    # thumbnail
    thumbnail_image = models.ImageField(_('Thumbnail'), blank=True,
                             null=True, upload_to=RESOURCES_STORAGE_PATH)

    # file
    xml_file = models.FileField(_('Resource file'),
                                upload_to=RESOURCES_STORAGE_PATH,
                                null=False)

    # counter
    download_count = models.IntegerField(_('Downloads'),
                                         default=0,
                                         editable=False)

    def get_resource_types(self):
        return ", ".join([_.name for _ in self.resource_types.all()])

    def __unicode__(self):
        return "%s" % (self.name)

    def __str__(self):
        return self.__unicode__()
