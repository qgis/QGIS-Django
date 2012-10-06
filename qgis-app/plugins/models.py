# -*- coding: utf-8 -*-
from django.db import models
# import auth users for owners
from django.contrib.auth.models import User
# i18n
from django.utils.translation import ugettext_lazy as _
# For permalinks
from django.core.urlresolvers import reverse
from django.conf import settings
import datetime, os, re

# Tagging
#from taggit.managers import TaggableManager
from taggit_autosuggest.managers import TaggableManager

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
        return super(StablePlugins, self).get_query_set().filter(pluginversion__approved=True, pluginversion__experimental=False).distinct()

class ExperimentalPlugins(models.Manager):
    """
    Shows only public plugins: i.e. those with "approved" flag set
    and with one "experimental" version
    """
    def get_query_set(self):
        return super(ExperimentalPlugins, self).get_query_set().filter(pluginversion__approved=True, pluginversion__experimental=True).distinct()

class FeaturedPlugins(models.Manager):
    """
    Shows only public featured stable plugins: i.e. those with "approved" flag set
    and "featured" flag set
    """
    def get_query_set(self):
        return super(FeaturedPlugins, self).get_query_set().filter(pluginversion__approved=True, featured=True).order_by('-created_on').distinct()

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
        return super(FreshPlugins, self).get_query_set().filter(pluginversion__approved=True, modified_on__gte = datetime.datetime.now()- datetime.timedelta(days = self.days)).order_by('-created_on').distinct()

class UnapprovedPlugins(models.Manager):
    """
    Shows only unapproved plugins
    """
    def get_query_set(self):
        return super(UnapprovedPlugins, self).get_query_set().filter(pluginversion__approved=False).distinct()


class DeprecatedPlugins(models.Manager):
    """
    Shows only deprecated plugins
    """
    def get_query_set(self):
        return super(DeprecatedPlugins, self).get_query_set().filter(deprecated=True).distinct()


class PopularPlugins(ApprovedPlugins):
    """
    Shows only unapproved plugins, sort by downloads
    """
    def get_query_set(self):
        return super(PopularPlugins, self).get_query_set().filter(deprecated=False ).order_by('-downloads').distinct()



class TaggablePlugins (TaggableManager):
    """
    Shows only public plugins: i.e. those with "approved" flag set
    """
    def get_query_set(self):
        return super(TaggablePlugnis, self).get_query_set().filter(deprecated=False, pluginversion__approved=True).distinct()

class Plugin (models.Model):
    """
    Plugins model    
    """

    # dates
    created_on      = models.DateTimeField(_('Created on'), auto_now_add=True, editable=False )
    modified_on     = models.DateTimeField(_('Modified on'), editable=False )

    # owners
    created_by      = models.ForeignKey(User, verbose_name=_('Created by'), related_name = 'plugins_created_by')
    author          = models.CharField(_('Author'), help_text=_('This is the plugin\'s original author, if different from the uploader, this field will appear in the XML and in the web GUI'), max_length=256)
    email           = models.EmailField(_('Author email'))
    homepage        = models.URLField(_('Plugin homepage'), verify_exists=False, blank=True, null=True)
    # Support
    repository      = models.URLField(_('Code repository'), verify_exists=False, blank=True, null=True)
    tracker         = models.URLField(_('Tracker'), verify_exists=False, blank=True, null=True)

    owners          = models.ManyToManyField(User, null=True, blank=True)

    # name, desc etc.
    package_name    = models.CharField(_('Package Name'), help_text=_('This is the plugin\'s internal name, equals to the main folder name'), max_length=256, unique=True, editable=False)
    name            = models.CharField(_('Name'), help_text=_('Must be unique'), max_length=256, unique=True)
    description     = models.TextField(_('Description'))

    icon            = models.ImageField(_('Icon'), blank=True, null=True, upload_to=PLUGINS_STORAGE_PATH)

    # downloads (soft trigger from versions)
    downloads       = models.IntegerField(_('Downloads'), default=0, editable=False)

    # Flags
    featured        = models.BooleanField(_('Featured'), default=False)
    deprecated      = models.BooleanField(_('Deprecated'), default=False)

    # Managers
    objects                 = models.Manager()
    approved_objects        = ApprovedPlugins()
    stable_objects          = StablePlugins()
    experimental_objects    = ExperimentalPlugins()
    featured_objects        = FeaturedPlugins()
    fresh_objects           = FreshPlugins()
    unapproved_objects      = UnapprovedPlugins()
    deprecated_objects      = DeprecatedPlugins()
    popular_objects         = PopularPlugins()

    tags                    = TaggableManager(blank=True)


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
        ordering = ('name',)
        # ABP: Note: this permission should belong to the
        # PluginVersion class. I left it here because it
        # doesn't really matters where it is. Just be
        # sure you query for it using the 'plugins' class
        # instead of the 'pluginversion' class.
        permissions = (
            ("can_approve", "Can approve plugins versions"),
        )

    def get_absolute_url(self):
        return reverse('plugin_detail', args=(self.package_name,))

    def __unicode__(self):
        return "[%s] %s" % (self.pk ,self.name)

    def __str__(self):
        return self.__unicode__()

    def clean(self):
        """
        Validates:

        * Checks that package_name respect regexp [A-Za-z][A-Za-z0-9-_]+
        * checks for case-insensitive unique package_name
        """
        from django.core.exceptions import ValidationError

        if not re.match(r'^[A-Za-z][A-Za-z0-9-_]+$', self.package_name):
           raise ValidationError(unicode(_('Plugin package_name (which equals to the main plugin folder inside the zip file) must start with an ASCII letter and can contain only ASCII letters, digits and the - and _ signs.')))

        if self.pk:
            qs = Plugin.objects.filter(name__iexact=self.name).exclude(pk=self.pk)
        else:
            qs = Plugin.objects.filter(name__iexact=self.name)
        if qs.count():
            raise ValidationError(unicode(_('A plugin with a similar name (%s) already exists (the name only differs in case).') % qs.all()[0].name))

        if self.pk:
            qs = Plugin.objects.filter(package_name__iexact=self.package_name).exclude(pk=self.pk)
        else:
            qs = Plugin.objects.filter(package_name__iexact=self.package_name)
        if qs.count():
            raise ValidationError(unicode(_('A plugin with a similar package_name (%s) already exists (the package_name only differs in case).') % qs.all()[0].package_name))



    def save(self, keep_date=False, *args, **kwargs):
        """
        Soft triggers:
        * updates modified_on if keep_date is not set
        """
        if self.pk and not keep_date:
            import logging
            logging.debug('Updating modified_on for the Plugin instance')
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
    created_on      = models.DateTimeField(_('Created on'),  auto_now_add=True, editable=False )
    # download counter
    downloads       = models.IntegerField(_('Downloads'), default=0, editable=False)
    # owners
    created_by      = models.ForeignKey(User, verbose_name=_('Created by'))
    # version info, the first should be read from plugin
    min_qg_version  = models.CharField(_('Minimum QGIS version'), max_length=32)
    version         = models.CharField(_('Version'), max_length=32)
    changelog       = models.TextField(_('Changelog'), null=True, blank=True)

    # the file!
    package         = models.FileField(_('Plugin package'), upload_to=PLUGINS_STORAGE_PATH)
    # Flags: checks on unique current/experimental are done in save() and possibly in the views
    experimental    = models.BooleanField(_('Experimental flag'), default=False, help_text=_("Check this box if this version is experimental, leave unchecked if it's stable."))
    approved        = models.BooleanField(_('Approved'), default=True, help_text=_('Set to false if you wish to unapprove the plugin version.'))

    @property
    def file_name(self):
        return os.path.basename(self.package.file.name)

    def save(self, *args, **kwargs):
        """
        Soft triggers:
        * updates modified_on in parent
        """

        # Transforms the version...
        # Need to be done here too, because clean()
        # is only called in forms.
        if self.version.rfind(' ') > 0:
            self.version = self.version.rsplit(' ')[-1]

        # Only change modified_on when a new version is created,
        # every download triggers a save to update the counter
        if not self.pk:
            self.plugin.modified_on = self.created_on
            self.plugin.save()

        super(PluginVersion, self).save(*args, **kwargs)

    def clean(self):
        """
        Validates:

        * checks for unique
        * checks for version only digits and dots
        """
        from django.core.exceptions import ValidationError

        # Transforms the version
        self.version = PluginVersion.clean_version(self.version)

        versions_to_check=PluginVersion.objects.filter(plugin=self.plugin, version=self.version)
        if self.pk:
            versions_to_check = versions_to_check.exclude(pk=self.pk)
        # Checks for unique_together
        if versions_to_check.filter(plugin=self.plugin, version=self.version).count() > 0:
            raise ValidationError(unicode(_('Version value must be unique among each plugin: a version with same number already exists.')))

    @staticmethod
    def clean_version(version):
        """
        Strips blanks and Version string
        """
        if version.rfind(' ') > 0:
            version = version.rsplit(' ')[-1]
        return version

    class Meta:
        unique_together = ('plugin', 'version')
        ordering = ('plugin',  '-version', 'experimental')

    def get_absolute_url(self):
        return reverse('version_detail', args=(self.plugin.package_name, self.version,))

    def get_download_url(self):
        return reverse('version_download', args=(self.plugin.package_name, self.version,))

    def download_file_name(self):
        return "%s.%s.zip" % (self.plugin.package_name, self.version)

    def __unicode__(self):
        desc = "%s %s" % (self.plugin ,self.version)
        if self.experimental:
            desc = "%s %s" % (desc, _('Experimental'))
        return desc

    def __str__(self):
        return self.__unicode__()


#class PluginCrashReport(models.Model):
    #"""
    #Plugin crash report
    #Input:
    #IP
    #package_name
    #version
    #backtrace
    #qg_version
    #SO
    #"""

    ## link to parent
    #plugin_version  = models.ForeignKey ( PluginVersion )
    ## dates
    #created_on      = models.DateTimeField(_('Created on'),  auto_now_add=True, editable=False )
    #created_by      = models.ForeignKey(User, blank=True, null=True, verbose_name=_('Created by'))
    ## version info, the first should be read from plugin
    #qg_version      = models.CharField(_('QGIS version'), max_length=32)
    #operating_system= models.CharField(_('Operating system'), max_length=15)
    #ip_address      = models.CharField(_('IP Address'), max_length=15)
    #backtrace       = models.TextField(_('Python backtrace'))


def delete_version_package(sender, instance, **kw):
    """
    Removes the zip package
    """
    try:
        os.remove(instance.package.path)
    except:
        pass

def delete_plugin_icon(sender, instance, **kw):
    """
    Removes the plugin icon
    """
    try:
        os.remove(instance.icon.path)
    except:
        pass

models.signals.post_delete.connect(delete_version_package, sender=PluginVersion)
models.signals.post_delete.connect(delete_plugin_icon, sender=Plugin)

