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

# Tagging
from taggit.managers import TaggableManager


PLUGINS_STORAGE_PATH = getattr(settings, 'PLUGINS_STORAGE_PATH', 'packages')
PLUGINS_FRESH_DAYS   = getattr(settings, 'PLUGINS_FRESH_DAYS', 30)

class ApprovedPlugins(models.Manager):
    """
    Shows only public plugins: i.e. those with
    and with at least one approved version ("stable" or "experimental")
    """
    def get_query_set(self):
        return super(ApprovedPlugins, self).get_query_set().filter(pluginversion__approved=True).distinct()

class StablePlugins(models.Manager):
    """
    Shows only public plugins: i.e. those with "approved" flag set
    and with one "stable" version
    """
    def get_query_set(self):
        return super(StablePlugins, self).get_query_set().filter(pluginversion__approved=True, pluginversion__experimental=False)

class ExperimentalPlugins(models.Manager):
    """
    Shows only public plugins: i.e. those with "approved" flag set
    and with one "experimental" version
    """
    def get_query_set(self):
        return super(ExperimentalPlugins, self).get_query_set().filter(pluginversion__approved=True, pluginversion__experimental=True)

class FeaturedPlugins(models.Manager):
    """
    Shows only public featured stable plugins: i.e. those with "approved" flag set
    with one "stable" version and "featured" flag set
    """
    def get_query_set(self):
        return super(FeaturedPlugins, self).get_query_set().filter(pluginversion__approved=True, featured=True, pluginversion__experimental=False)

class FreshPlugins(models.Manager):
    """
    Shows only approved plugins: i.e. those with "approved" version flag set
    and modified less than "days" ago.
    A Plugin is modified even when a new version is uploaded
    """
    def __init__(self, days = PLUGINS_FRESH_DAYS, *args, **kwargs):
        self.days = days
        return super(FreshPlugins, self).__init__(*args, **kwargs)

    def get_query_set(self):
        return super(FreshPlugins, self).get_query_set().filter(pluginversion__approved=True, modified_on__gte = datetime.datetime.now()- datetime.timedelta(days = self.days)).distinct()

class UnapprovedPlugins(models.Manager):
    """
    Shows only unapproved plugins
    """
    def get_query_set(self):
        return super(UnapprovedPlugins, self).get_query_set().filter(pluginversion__approved=False).distinct()


class PopularPlugins(ApprovedPlugins):
    """
    Shows only unapproved plugins, sort by downloads
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
    created_on      = models.DateTimeField(_('Created on'), auto_now_add=True, editable=False )
    modified_on     = models.DateTimeField(_('Modified on'), editable=False )

    # owners
    created_by      = models.ForeignKey(User, verbose_name = _('Created by'), related_name = 'plugins_created_by')
    homepage        = models.URLField(_('Plugin homepage'), verify_exists=False, blank=True, null=True)
    owners          = models.ManyToManyField(User, null=True, blank=True)

    # name, desc etc.
    package_name    = models.CharField(_('Package Name'), help_text = _('This is the plugin\'s internal name, equals to the main folder name'), max_length = 256, unique=True, editable=False)
    name            = models.CharField(_('Name'), help_text = _('Must be unique'), max_length = 256, unique=True)
    description     = models.TextField(_('Description'))

    icon            = models.ImageField(_('Icon'), blank=True, null=True, upload_to = PLUGINS_STORAGE_PATH)

    # downloads (soft trigger from versions)
    downloads       = models.IntegerField(_('Downloads'), default = 0, editable=False)

    # Flags
    featured        = models.BooleanField(_('Featured'), default=False)

    # Managers
    objects                 = models.Manager()
    approved_objects        = ApprovedPlugins()
    stable_objects          = StablePlugins()
    experimental_objects    = ExperimentalPlugins()
    featured_objects        = FeaturedPlugins()
    fresh_objects           = FreshPlugins()
    unapproved_objects      = UnapprovedPlugins()
    popular_objects         = PopularPlugins()

    tags = TaggableManager()


    @property
    def approved(self):
        """
        Returns True if the plugin has at least one approved version
        """
        return self.pluginversion_set.filter(approved=True).count() > 0

    @property
    def trusted(self):
        """
        Returns True if the plugin's author has plugins.can_approve permission
        Purpose of this decorator is to show/hide buttons in the template
        """
        return self.created_by.has_perm('plugins.can_approve')

    @property
    def stable(self):
        """
        Returns the latest stable and approved version
        """
        try:
            return self.pluginversion_set.filter(approved=True, experimental=False).order_by('-version')[0]
        except:
            return None

    @property
    def experimental(self):
        """
        Returns the latest experimental and approved version
        """
        try:
            return self.pluginversion_set.filter(approved=True, experimental=True).order_by('-version')[0]
        except:
            return None

    @property
    def editors(self):
        """
        Returns a list of users that can edit the plugin: creator and owners
        """
        l = [o for o in self.owners.all()]
        l.append(self.created_by)
        return l

    @property
    def approvers(self):
        """
        Returns a list of editor users that can approve a version
        """
        return [l for l in self.editors if l.has_perm('plugins.can_approve')]

    class Meta:
        ordering = ('featured', 'name' , 'modified_on')
        permissions = (
            ("can_approve", "Can approve plugins"),
        )

    def get_absolute_url(self):
        return reverse('plugin_detail', args=(self.pk,))

    def __unicode__(self):
        return "[%s] %s" % (self.pk ,self.name)

    def __str__(self):
        return self.__unicode__()

    def save(self, keep_date=False, *args, **kwargs):
        """
        Soft triggers:
        * updates modified_on if keep_date is not set
        """
        if self.pk and not keep_date:
            import logging
            logging.debug('setting date')
            self.modified_on = datetime.datetime.now()
        if not self.pk:
          self.modified_on = datetime.datetime.now()
        super(Plugin, self).save(*args, **kwargs)



class PluginVersion (models.Model):
    """
    Plugin versions
    """

    # link to parent
    plugin          = models.ForeignKey ( Plugin )
    # dates
    created_on      = models.DateTimeField(_('Created on'),  auto_now_add=True,  editable=False )
    # download counter
    downloads       = models.IntegerField(_('Downloads'), default = 0, editable=False)
    # owners
    created_by      = models.ForeignKey(User, verbose_name = _('Created by'))
    # version info, the first should be read from plugin
    min_qg_version  = models.CharField(_('Minimum QGIS version'), max_length = 32)
    version         = models.CharField(_('Version'), max_length = 32)
    changelog       = models.TextField(_('Changelog'))

    # the file!
    package         = models.FileField(_('Plugin package'), upload_to = PLUGINS_STORAGE_PATH)
    # Flags: checks on unique current/experimental are done in save() and possibly in the views
    experimental    = models.BooleanField(_('Experimental flag'), default=False, help_text=_("Check this box if this version is experimental, leave unchecked if it's stable"))
    approved        = models.BooleanField(_('Approved'), default=True, help_text=_('Set to false if you wish to unapprova the plugin version.'))

    @property
    def file_name(self):
        return os.path.basename(self.package.file.name)

    def save(self, *args, **kwargs):
        """
        Soft triggers:
        * updates modified_on in parent
        """

        # Only change modified_on when a new version is created,
        # every download triggers a save to update the counter
        if not self.pk:
            self.plugin.modified_on = self.created_on
            self.plugin.save()

        super(PluginVersion, self).save(*args, **kwargs)

    def clean(self):
        """
        Validates:
        checks for unique
        """
        from django.core.exceptions import ValidationError

        versions_to_check=PluginVersion.objects.filter(plugin = self.plugin, experimental=self.experimental)
        if self.pk:
            versions_to_check = versions_to_check.exclude(pk = self.pk)
        # Checks for unique_together
        if versions_to_check.filter(plugin=self.plugin, version=self.version).count() > 0:
            raise ValidationError(unicode(_('Version value must be unique for this plugin.')))


    class Meta:
        unique_together = ('plugin', 'version')
        ordering = ('plugin',  'version', '-created_on' , 'experimental')

    def get_absolute_url(self):
        return reverse('version_detail', args=(self.pk,))

    def get_download_url(self):
        return reverse('version_download', args=(self.pk,))

    def __unicode__(self):
        desc = "%s %s" % (self.plugin ,self.version)
        if self.experimental:
            desc = "%s %s" % (desc, _('Experimental'))
        return desc

    def __str__(self):
        return self.__unicode__()

