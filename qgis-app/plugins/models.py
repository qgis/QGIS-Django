# -*- coding: utf-8 -*-

import datetime, os, re

from django.db import models
# import auth users for owners
from django.contrib.auth.models import User
# i18n
from django.utils.translation import ugettext_lazy as _
# For permalinks
from django.core.urlresolvers import reverse
from django.conf import settings
from djangoratings.fields import AnonymousRatingField

# Tagging
from taggit_autosuggest.managers import TaggableManager

PLUGINS_STORAGE_PATH = getattr(settings, 'PLUGINS_STORAGE_PATH', 'packages/%Y')
PLUGINS_FRESH_DAYS   = getattr(settings, 'PLUGINS_FRESH_DAYS', 30)


# Used in Version fields to transform DB value back to human readable string
VERSION_RE=r'(^|(?<=\.))0+(?!(\.|$))|\.#+'

class BasePluginManager(models.Manager):
    """
    Adds a score
    """
    def get_query_set(self):
        return super(BasePluginManager, self).get_query_set().extra(
            select={
                'average_vote': 'rating_score/(rating_votes+0.001)'
            })

class ApprovedPlugins(BasePluginManager):
    """
    Shows only public plugins: i.e. those with
    and with at least one approved version ("stable" or "experimental")
    """
    def get_query_set(self):
        return super(ApprovedPlugins, self).get_query_set().filter(pluginversion__approved=True).distinct()


class StablePlugins(BasePluginManager):
    """
    Shows only public plugins: i.e. those with "approved" flag set
    and with one "stable" version
    """
    def get_query_set(self):
        return super(StablePlugins, self).get_query_set().filter(pluginversion__approved=True, pluginversion__experimental=False).distinct()


class ExperimentalPlugins(BasePluginManager):
    """
    Shows only public plugins: i.e. those with "approved" flag set
    and with one "experimental" version
    """
    def get_query_set(self):
        return super(ExperimentalPlugins, self).get_query_set().filter(pluginversion__approved=True, pluginversion__experimental=True).distinct()


class FeaturedPlugins(BasePluginManager):
    """
    Shows only public featured stable plugins: i.e. those with "approved" flag set
    and "featured" flag set
    """
    def get_query_set(self):
        return super(FeaturedPlugins, self).get_query_set().filter(pluginversion__approved=True, featured=True).order_by('-created_on').distinct()


class FreshPlugins(BasePluginManager):
    """
    Shows only approved plugins: i.e. those with "approved" version flag set
    and modified less than "days" ago.
    A Plugin is modified even when a new version is uploaded
    """
    def __init__(self, days = PLUGINS_FRESH_DAYS, *args, **kwargs):
        self.days = days
        return super(FreshPlugins, self).__init__(*args, **kwargs)

    def get_query_set(self):
        return super(FreshPlugins, self).get_query_set().filter(deprecated=False, pluginversion__approved=True, modified_on__gte = datetime.datetime.now()- datetime.timedelta(days = self.days)).order_by('-created_on').distinct()


class UnapprovedPlugins(BasePluginManager):
    """
    Shows only unapproved plugins
    """
    def get_query_set(self):
        return super(UnapprovedPlugins, self).get_query_set().filter(pluginversion__approved=False).distinct()


class DeprecatedPlugins(BasePluginManager):
    """
    Shows only deprecated plugins
    """
    def get_query_set(self):
        return super(DeprecatedPlugins, self).get_query_set().filter(deprecated=True).distinct()



class PopularPlugins(ApprovedPlugins):
    """
    Shows only approved plugins, sort by popularity algorithm
    """
    def get_query_set(self):
        return super(PopularPlugins, self).get_query_set().filter(deprecated=False).extra(
            select={
                'popularity': 'plugins_plugin.downloads * (1 + (rating_score/(rating_votes+0.01)/3))'
            }
        ).order_by('-popularity').distinct()


class MostDownloadedPlugins(ApprovedPlugins):
    """
    Shows only approved plugins, sort by downloads
    """
    def get_query_set(self):
        return super(MostDownloadedPlugins, self).get_query_set().filter(deprecated=False).order_by('-downloads').distinct()


class MostVotedPlugins(ApprovedPlugins):
    """
    Shows only approved plugins, sort by vote number
    """
    def get_query_set(self):
        return super(MostVotedPlugins, self).get_query_set().filter(deprecated=False).order_by('-rating_votes').distinct()


class MostRatedPlugins(ApprovedPlugins):
    """
    Shows only approved plugins, sort by vote/number of votes number
    """
    def get_query_set(self):
        return super(ApprovedPlugins, self).get_query_set().filter(deprecated=False).order_by('-average_vote').distinct()


class TaggablePlugins(TaggableManager):
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
    homepage        = models.URLField(_('Plugin homepage'), blank=True, null=True)
    # Support
    repository      = models.URLField(_('Code repository'), blank=True, null=True)
    tracker         = models.URLField(_('Tracker'), blank=True, null=True)

    owners          = models.ManyToManyField(User, null=True, blank=True)

    # name, desc etc.
    package_name    = models.CharField(_('Package Name'), help_text=_('This is the plugin\'s internal name, equals to the main folder name'), max_length=256, unique=True, editable=False)
    name            = models.CharField(_('Name'), help_text=_('Must be unique'), max_length=256, unique=True)
    description     = models.TextField(_('Description'))
    about           = models.TextField(_('About'), blank=True, null=True)

    icon            = models.ImageField(_('Icon'), blank=True, null=True, upload_to=PLUGINS_STORAGE_PATH)

    # downloads (soft trigger from versions)
    downloads       = models.IntegerField(_('Downloads'), default=0, editable=False)

    # Flags
    featured        = models.BooleanField(_('Featured'), default=False, db_index=True)
    deprecated      = models.BooleanField(_('Deprecated'), default=False, db_index=True)

    # Managers
    objects                 = models.Manager()
    base_objects            = BasePluginManager()
    approved_objects        = ApprovedPlugins()
    stable_objects          = StablePlugins()
    experimental_objects    = ExperimentalPlugins()
    featured_objects        = FeaturedPlugins()
    fresh_objects           = FreshPlugins()
    unapproved_objects      = UnapprovedPlugins()
    deprecated_objects      = DeprecatedPlugins()
    popular_objects         = PopularPlugins()
    most_downloaded_objects = MostDownloadedPlugins()
    most_voted_objects      = MostVotedPlugins()
    most_rated_objects      = MostRatedPlugins()

    rating                  = AnonymousRatingField(range=5, use_cookies=True, can_change_vote=True, allow_delete=True)

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


    @property
    def avg_vote(self):
        """
        Returns the rating_score/(rating_votes+0.001) value, this
        calculation is also available in manager's queries as
        "average_vote".
        This property is still useful when the object is not loaded
        through a manager, for example in related objects.
        """
        return self.rating_score/(self.rating_votes+0.001)

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



# Plugin version managers



class ApprovedPluginVersions(models.Manager):
    """
    Shows only public plugin versions:
    """
    def get_query_set(self):
        return super(ApprovedPluginVersions, self).get_query_set().filter(approved=True).order_by('-version')


class StablePluginVersions(ApprovedPluginVersions):
    """
    Shows only approved public plugin versions: i.e. those with "approved" flag set
    and with "stable" flag
    """
    def get_query_set(self):
        return super(StablePluginVersions, self).get_query_set().filter(experimental=False)


class ExperimentalPluginVersions(ApprovedPluginVersions):
    """
    Shows only public plugin versions: i.e. those with "approved" flag set
    and with  "experimental" flag
    """
    def get_query_set(self):
        return super(ExperimentalPluginVersions, self).get_query_set().filter(experimental=True)



def vjust(str, level=3, delim='.', bitsize=3, fillchar=' ', force_zero=False):
    """
    Normalize a dotted version string.

    1.12 becomes : 1.    12
    1.1  becomes : 1.     1


    if force_zero=True and level=2:

    1.12 becomes : 1.    12.     0
    1.1  becomes : 1.     1.     0


    """
    if not str:
        return str
    nb = str.count(delim)
    if nb < level:
        if force_zero:
            str += (level-nb) * (delim+'0')
        else:
            str += (level-nb) * delim
    parts = []
    for v in str.split(delim)[:level+1]:
        if not v:
            parts.append(v.rjust(bitsize,'#'))
        else:
            parts.append(v.rjust(bitsize,fillchar))
    return delim.join(parts)




class VersionField(models.CharField):


    description = 'Field to store version strings ("a.b.c.d") in a way it is sortable'

    __metaclass__ = models.SubfieldBase

    def get_prep_value(self, value):
        return vjust(value, fillchar='0')

    def to_python(self, value):
        if not value:
            return ''
        return re.sub(VERSION_RE, '', value)


class QGVersionZeroForcedField(models.CharField) :


    description = 'Field to store version strings ("a.b.c.d") in a way it \
    is sortable and QGIS scheme compatible (x.y.z).'

    __metaclass__ = models.SubfieldBase

    def get_prep_value(self, value):
        return vjust(value,fillchar='0',level=2,force_zero=True)

    def to_python(self, value):
        if not value:
            return ''
        return re.sub(VERSION_RE, '', value)


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
    min_qg_version  = QGVersionZeroForcedField(_('Minimum QGIS version'), max_length=32, db_index=True)
    max_qg_version  = QGVersionZeroForcedField(_('Maximum QGIS version'), max_length=32, null=True, blank=True, db_index=True)
    version         = VersionField(_('Version'), max_length=32, db_index=True)
    changelog       = models.TextField(_('Changelog'), null=True, blank=True)

    # the file!
    package         = models.FileField(_('Plugin package'), upload_to=PLUGINS_STORAGE_PATH)
    # Flags: checks on unique current/experimental are done in save() and possibly in the views
    experimental    = models.BooleanField(_('Experimental flag'), default=False, help_text=_("Check this box if this version is experimental, leave unchecked if it's stable."), db_index=True)
    approved        = models.BooleanField(_('Approved'), default=True, help_text=_('Set to false if you wish to unapprove the plugin version.'), db_index=True)

    # Managers, used in xml output
    objects                 = models.Manager()
    approved_objects        = ApprovedPluginVersions()
    stable_objects          = StablePluginVersions()
    experimental_objects    = ExperimentalPluginVersions()


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

        # fix Max version
        if not self.max_qg_version:
            self.max_qg_version = "%s.99" % tuple(self.min_qg_version.split('.')[0] )

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


from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^plugins\.models\.QGVersionZeroForcedField"])
add_introspection_rules([], ["^plugins\.models\.VersionField"])
