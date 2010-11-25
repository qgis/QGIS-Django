# -*- coding: utf-8 -*-
from django.db import models
# import auth users for owners
from django.contrib.auth.models import User
# i18n
from django.utils.translation import ugettext_lazy as _
# For permalinks
from django.core.urlresolvers import reverse

class Plugin (models.Model):
    """
    Plugins model
    # TODO: category, MPTT?
    # TODO: links to Plugin's page, trac etc.
    # TODO: managers
    """

    # dates
    created_on      = models.DateTimeField(_('Created on'),  auto_now_add = True,  editable = False )
    modified_on     = models.DateTimeField(_('Modified on'), auto_now = True, editable = False )

    # owners
    created_by      = models.ForeignKey(User, verbose_name = _('Created by'), related_name = 'plugins_created_by')
    owners          = models.ManyToManyField(User)

    # name, desc etc.
    name            = models.CharField(_('Name'), help_text = _('Internal name, must be unique'), max_length = 256, unique = True)
    title           = models.CharField(_('Title'), max_length = 256, unique = True)
    description     = models.TextField(_('Description'))

    @property
    def stable(self):
        return self.pluginversion_set.get(last = True, experimental = False)

    @property
    def experimental(self):
        return self.pluginversion_set.get(last = True, experimental = True)

    @property
    def downloads(self):
        return self.pluginversion_set.aggregate(models.Sum('downloads'))['downloads__sum']

    # Flags
    published       = models.BooleanField(_('Published'), default = True, help_text = _('Set to false if you wish to unpublish the plugin'))
    featured        = models.BooleanField(_('Featured'), default = False)

    class Meta:
        ordering = ('featured', 'title' , 'modified_on')
        permissions = (
            ("can_publish", "Can publish plugins"),
        )

    def get_absolute_url(self):
        return reverse('plugin_detail', args=(self.pk,))

    def __unicode__(self):
        return "[%s] %s" % (self.pk ,self.name)

    def __str__(self):
        return self.__unicode__()

class PluginVersion (models.Model):
    """
    Plugin versions
    """

    # link to parent
    plugin          = models.ForeignKey ( Plugin )
    # dates
    created_on      = models.DateTimeField(_('Created on'),  auto_now_add = True,  editable = False )
    # download counter
    downloads       = models.IntegerField(_('Downloads'), default = 0, editable = False)
    # owners
    created_by      = models.ForeignKey(User, verbose_name = _('Created by'))
    # version info, the first should be read from plugin
    min_qg_version  = models.CharField(_('Minimum QGIS version'), max_length = 32)
    version         = models.CharField(_('Version'), max_length = 32)
    changelog       = models.TextField(_('Changelog'))

    # the file!
    package         = models.FileField(_('Plugin package'), upload_to = 'static/packages')
    # Flags TODO: checks on unique last/experimental
    experimental    = models.BooleanField(_('Experimental flag'), default = False, help_text = _("Check this box if this version is experimental, leave unchecked if it's stable"))
    last            = models.BooleanField(_('Last flag'), default = True, help_text = _('Check this box if this version is the latest'))

    def save(self, *args, **kwargs):
        """
        Soft trigger: ensures that last is unique (among experimental and stable = not experimental)
        Update modified_on in parent
        """
        versions_to_check = PluginVersion.objects.filter(plugin = self.plugin, experimental = self.experimental)

        # Onli change modified_on when a new version is created,
        # each download triggers a save
        if self.pk:
            versions_to_check = versions_to_check.exclude(pk = self.pk)
        else:
            self.plugin.modified_on = self.created_on

        if self.last:
            for p in versions_to_check:
                p.last = False
                p.save()
        super(PluginVersion, self).save(*args, **kwargs)

    def clean(self):
        """
        Validates that exists one last version in the experimental/stable "branch"
        """
        from django.core.exceptions import ValidationError
        versions_to_check = PluginVersion.objects.filter(plugin = self.plugin, experimental = self.experimental)
        if self.pk:
            versions_to_check = versions_to_check.exclude(pk = self.pk)
        if not (self.last or versions_to_check.filter(last = True).count()):
            raise ValidationError(unicode(_('At least one version must be checked as "last" among experimental and not-experimental plugin versions.')))

    class Meta:
        unique_together = ('plugin', 'version', 'experimental')

    def get_absolute_url(self):
        return reverse('version_detail', args=(self.pk))

    def __unicode__(self):
        desc = "%s %s" % (self.plugin ,self.version)
        if self.last:
            desc = "%s %s" % (desc, _('Last'))
        if self.experimental:
            desc = "%s %s" % (desc, _('Experimental'))
        return desc

    def __str__(self):
        return self.__unicode__()

