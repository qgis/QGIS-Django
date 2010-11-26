# -*- coding: utf-8 -*-
from django.db import models
# import auth users for owners
from django.contrib.auth.models import User
# i18n
from django.utils.translation import ugettext_lazy as _
# For permalinks
from django.core.urlresolvers import reverse
from django.conf import settings
import datetime, os


PLUGINS_STORAGE_PATH = getattr(settings, 'PLUGINS_STORAGE_PATH', 'packages')
PLUGINS_FRESH_DAYS   = getattr(settings, 'PLUGINS_FRESH_DAYS', 30)

class PublishedPlugins(models.Manager):
    """
    Shows only public plugins: i.e. those with "published" flag set
    and with at least one version ("stable" or "experimental")
    """
    def get_query_set(self):
        return super(PublishedPlugins, self).get_query_set().filter(published = True, pluginversion__last = True).distinct()

class StablePlugins(models.Manager):
    """
    Shows only public plugins: i.e. those with "published" flag set
    and with one "stable" version
    """
    def get_query_set(self):
        return super(StablePlugins, self).get_query_set().filter(published = True, pluginversion__last = True, pluginversion__experimental = False)

class ExperimentalPlugins(models.Manager):
    """
    Shows only public plugins: i.e. those with "published" flag set
    and with one "experimental" version
    """
    def get_query_set(self):
        return super(ExperimentalPlugins, self).get_query_set().filter(published = True, pluginversion__last = True, pluginversion__experimental = True)

class FeaturedPlugins(models.Manager):
    """
    Shows only public featured stable plugins: i.e. those with "published" flag set
    with one "stable" version and "featured" flag set
    """
    def get_query_set(self):
        return super(FeaturedPlugins, self).get_query_set().filter(published = True, featured = True, pluginversion__last = True, pluginversion__experimental = False)

class FreshPlugins(models.Manager):
    """
    Shows only public plugins: i.e. those with "published" flag set
    and modified less than "days" ago.
    A Plugin is modified even when a new version is uploaded
    """
    def __init__(self, days = PLUGINS_FRESH_DAYS, *args, **kwargs):
        self.days = days
        return super(FreshPlugins, self).__init__(*args, **kwargs)

    def get_query_set(self):
        return super(FreshPlugins, self).get_query_set().filter(published = True, pluginversion__last = True, modified_on__gte = datetime.datetime.now()- datetime.timedelta(days = self.days)).distinct()

class UnpublishedPlugins(models.Manager):
    """
    Shows only unpublished plugins
    """
    def get_query_set(self):
        return super(UnpublishedPlugins, self).get_query_set().filter(published = False)


class PopularPlugins(PublishedPlugins):
    """
    Shows only unpublished plugins, sort by downloads
    """
    def get_query_set(self):
        return super(PopularPlugins, self).get_query_set().order_by('-downloads')




class Plugin (models.Model):
    """
    Plugins model
    # TODO: category, MPTT?
    # TODO: links to Plugin's page, trac etc.
    """

    # dates
    created_on      = models.DateTimeField(_('Created on'),  auto_now_add = True,  editable = False )
    modified_on     = models.DateTimeField(_('Modified on'), auto_now = True, editable = False )

    # owners
    created_by      = models.ForeignKey(User, verbose_name = _('Created by'), related_name = 'plugins_created_by')
    homepage        = models.URLField(_('Plugin homepage'), verify_exists = False, blank = True, null = True)
    owners          = models.ManyToManyField(User)

    # name, desc etc.
    name            = models.CharField(_('Name'), help_text = _('Must be unique'), max_length = 256, unique = True)
    description     = models.TextField(_('Description'))

    # downloads (soft trigger from versions)
    downloads       = models.IntegerField(_('Downloads'), default = 0, editable = False)

    @property
    def trusted(self):
        """
        Returns True if the author has plugins.can_publish permission
        """
        return self.created_by.has_perm('plugins.can_publish')

    @property
    def stable(self):
        try:
            return self.pluginversion_set.get(last = True, experimental = False)
        except:
            return None

    @property
    def experimental(self):
        try:
            return self.pluginversion_set.get(last = True, experimental = True)
        except:
            return None

    # Flags
    published       = models.BooleanField(_('Published'), default = True, help_text = _('Set to false if you wish to unpublish the plugin'))
    featured        = models.BooleanField(_('Featured'), default = False)

    # Managers
    objects                 = models.Manager()
    published_objects       = PublishedPlugins()
    stable_objects          = StablePlugins()
    experimental_objects    = ExperimentalPlugins()
    featured_objects        = FeaturedPlugins()
    fresh_objects           = FreshPlugins()
    unpublished_objects     = UnpublishedPlugins()
    popular_objects         = PopularPlugins()

    class Meta:
        ordering = ('featured', 'name' , 'modified_on')
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
    package         = models.FileField(_('Plugin package'), upload_to = PLUGINS_STORAGE_PATH)
    # Flags TODO: checks on unique last/experimental
    experimental    = models.BooleanField(_('Experimental flag'), default = False, help_text = _("Check this box if this version is experimental, leave unchecked if it's stable"))
    last            = models.BooleanField(_('Last flag'), default = True, help_text = _('Check this box if this version is the latest'))

    @property
    def file_name(self):
        return os.path.basename(self.package.file.name)

    def save(self, *args, **kwargs):
        """
        Soft trigger: ensures that last is unique (among experimental and stable = not experimental)
        Updates modified_on in parent
        """
        versions_to_check = PluginVersion.objects.filter(plugin = self.plugin, experimental = self.experimental)

        # Only change modified_on when a new version is created,
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
        ordering = ('plugin', '-created_on' , 'experimental')

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

