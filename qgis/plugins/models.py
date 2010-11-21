# -*- coding: utf-8 -*-
from django.db import models

# import auth users for owners
from django.contrib.auth.models import User

# i18n
from django.utils.translation import ugettext_lazy as _

class Plugin (models.Model):
    """
    Plugins model
    """

    # dates
    created_on      = models.DateTimeField(_('Created on'),  auto_now_add = True,  editable = False )
    modified_on     = models.DateTimeField(_('Modified on'), auto_now = True, editable = False )

    # owners
    created_by      = models.ForeignKey(User, verbose_name = _('Created by'),
            related_name = 'plugins_created_by')
    owners          = models.ManyToManyField(User)

    # download counter
    downloads       = models.IntegerField(_('Downloads'), default = 0)

    # name, desc etc.
    name            = models.CharField(_('Name'), max_length = 256, unique =
            True)
    description     = models.TextField(_('Description'))

    # TODO: category, MPTT?
    # TODO: links to Plugin's page, trac etc.

    # Flags
    published       = models.BooleanField(_('Published'), default = True,
        help_text = _('Set to false if you wish to unpublish the plugin'))
    featured        = models.BooleanField(_('Featured'), default = False)

    def __unicode__(self):
        return "%s %s" % (self.pk ,self.name)

    def __str__(self):
        return self.__unicode__()

class PluginVersion (models.Model):
    """
    Plugin versions
    """

    # link to parent
    plugin          = models.ForeignKey ( Plugin )

    # dates
    created_on      = models.DateTimeField(_('Created on'),  auto_now_add =
        True,  editable = False )

    # owners
    created_by      = models.ForeignKey(User, verbose_name = _('Created by'))

    # version info, the first should be read from plugin
    min_qg_version  = models.CharField(_('Minimum QGIS version'), editable =
        False, max_length = 32)
    version         = models.CharField(_('Version'), max_length = 32)

    # the file!
    package         = models.FileField(_('Plugin package'), upload_to =
    'packages')

    # Flags TODO: checks on unique last/experimental
    experimental    = models.BooleanField(_('Experimental'), default = False)
    last            = models.BooleanField(_('Last'), default = True, help_text
        = _('Check this box if this version is the latest'))

    class Meta:
        unique_together = ('plugin', 'version')

    def __unicode__(self):
        return "%s %s" % (self.plugin ,self.version)

    def __str__(self):
        return self.__unicode__()

