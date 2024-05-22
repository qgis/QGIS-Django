# -*- coding: utf-8 -*-

import datetime
import os
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from djangoratings.fields import AnonymousRatingField
from taggit_autosuggest.managers import TaggableManager
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

PLUGINS_STORAGE_PATH = getattr(settings, "PLUGINS_STORAGE_PATH", "packages/%Y")
PLUGINS_FRESH_DAYS = getattr(settings, "PLUGINS_FRESH_DAYS", 30)


# Used in Version fields to transform DB value back to human readable string
# Allows "-" for processing plugin
VERSION_RE = r"(^|(?<=\.))0+(?!(\.|$|-))|\.#+"


class BasePluginManager(models.Manager):
    """
    Adds a score
    """

    def get_queryset(self):
        return (
            super(BasePluginManager, self)
            .get_queryset()
            .extra(
                select={
                    "average_vote": "rating_score/(rating_votes+0.001)",
                    "latest_version_date": (
                        "SELECT created_on FROM plugins_pluginversion WHERE "
                        "plugins_pluginversion.plugin_id = plugins_plugin.id "
                        "AND approved = TRUE "
                        "ORDER BY created_on DESC LIMIT 1"
                    ),
                }
            )
        )


class ApprovedPlugins(BasePluginManager):
    """
    Shows only public plugins: i.e. those with
    and with at least one approved version ("stable" or "experimental")
    """

    def get_queryset(self):
        return (
            super(ApprovedPlugins, self)
            .get_queryset()
            .filter(pluginversion__approved=True)
            .distinct()
        )


class StablePlugins(BasePluginManager):
    """
    Shows only public plugins: i.e. those with "approved" flag set
    and with one "stable" version
    """

    def get_queryset(self):
        return (
            super(StablePlugins, self)
            .get_queryset()
            .filter(pluginversion__approved=True, pluginversion__experimental=False)
            .distinct()
        )


class ExperimentalPlugins(BasePluginManager):
    """
    Shows only public plugins: i.e. those with "approved" flag set
    and with one "experimental" version
    """

    def get_queryset(self):
        return (
            super(ExperimentalPlugins, self)
            .get_queryset()
            .filter(pluginversion__approved=True, pluginversion__experimental=True)
            .distinct()
        )


class FeaturedPlugins(BasePluginManager):
    """
    Shows only public featured stable plugins: i.e. those with "approved" flag set
    and "featured" flag set
    """

    def get_queryset(self):
        return (
            super(FeaturedPlugins, self)
            .get_queryset()
            .filter(pluginversion__approved=True, featured=True)
            .order_by("-created_on")
            .distinct()
        )


class FreshPlugins(BasePluginManager):
    """
    Shows only approved plugins: i.e. those with "approved" version flag set
    and created less than "days" ago.
    """

    def __init__(self, days=PLUGINS_FRESH_DAYS, *args, **kwargs):
        self.days = days
        return super(FreshPlugins, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return (
            super(FreshPlugins, self)
            .get_queryset()
            .filter(
                deprecated=False,
                pluginversion__approved=True,
                created_on__gte=datetime.datetime.now()
                - datetime.timedelta(days=self.days),
            )
            .order_by("-created_on")
            .distinct()
        )


class LatestPlugins(BasePluginManager):
    """
    Shows only approved plugins ordered descending by latest_version
    and the latest_version
    """

    def __init__(self, days=PLUGINS_FRESH_DAYS, *args, **kwargs):
        self.days = days
        return super(LatestPlugins, self).__init__(*args, **kwargs)

    def get_queryset(self):
        return (
            super(LatestPlugins, self)
            .get_queryset()
            .filter(
                deprecated=False,
                pluginversion__approved=True,
                pluginversion__created_on__gte=(
                    datetime.datetime.now() - datetime.timedelta(days=self.days)
                ),
            )
            .order_by("-latest_version_date")
            .distinct()
        )


class UnapprovedPlugins(BasePluginManager):
    """
    Shows only unapproved and not deprecated plugins
    """

    def get_queryset(self):
        return (
            super(UnapprovedPlugins, self)
            .get_queryset()
            .filter(pluginversion__approved=False, deprecated=False)
            .distinct()
        )


class DeprecatedPlugins(BasePluginManager):
    """
    Shows only deprecated plugins
    """

    def get_queryset(self):
        return (
            super(DeprecatedPlugins, self)
            .get_queryset()
            .filter(deprecated=True)
            .distinct()
        )


class PopularPlugins(ApprovedPlugins):
    """
    Shows only approved plugins, sort by popularity algorithm
    """

    def get_queryset(self):
        return (
            super(PopularPlugins, self)
            .get_queryset()
            .filter(deprecated=False)
            .extra(
                select={
                    "popularity": "plugins_plugin.downloads * (1 + (rating_score/(rating_votes+0.01)/3))"
                }
            )
            .order_by("-popularity")
            .distinct()
        )


class MostDownloadedPlugins(ApprovedPlugins):
    """
    Shows only approved plugins, sort by downloads
    """

    def get_queryset(self):
        return (
            super(MostDownloadedPlugins, self)
            .get_queryset()
            .filter(deprecated=False)
            .order_by("-downloads")
            .distinct()
        )


class MostVotedPlugins(ApprovedPlugins):
    """
    Shows only approved plugins, sort by vote number
    """

    def get_queryset(self):
        return (
            super(MostVotedPlugins, self)
            .get_queryset()
            .filter(deprecated=False)
            .order_by("-rating_votes")
            .distinct()
        )


class MostRatedPlugins(ApprovedPlugins):
    """
    Shows only approved plugins, sort by vote/number of votes number
    """

    def get_queryset(self):
        return (
            super(MostRatedPlugins, self)
            .get_queryset()
            .filter(deprecated=False)
            .order_by("-average_vote")
            .distinct()
        )


class TaggablePlugins(TaggableManager):
    """
    Shows only public plugins: i.e. those with "approved" flag set
    """

    def get_queryset(self):
        return (
            super(TaggablePlugins, self)
            .get_queryset()
            .filter(deprecated=False, pluginversion__approved=True)
            .distinct()
        )


class ServerPlugins(ApprovedPlugins):
    """
    Shows only Server plugins
    """

    def get_queryset(self):
        return super(ServerPlugins, self).get_queryset().filter(server=True).distinct()


class FeedbackReceivedPlugins(models.Manager):
    """
    Show only unapproved plugins with a feedback
    """
    def get_queryset(self):
        return (
            super(FeedbackReceivedPlugins, self)
            .get_queryset()
            .filter(
                pluginversion__approved=False,
                pluginversion__feedback__isnull=False
            ).distinct()
        )


class FeedbackPendingPlugins(models.Manager):
    """
    Show only unapproved plugins with a feedback
    """
    def get_queryset(self):
        return (
            super(FeedbackPendingPlugins, self)
            .get_queryset()
            .filter(
                pluginversion__approved=False,
                pluginversion__feedback__isnull=True
            ).distinct()
        )



class Plugin(models.Model):
    """
    Plugins model
    """

    # dates
    created_on = models.DateTimeField(
        _("Created on"), auto_now_add=True, editable=False
    )
    modified_on = models.DateTimeField(_("Modified on"), editable=False)

    # owners
    created_by = models.ForeignKey(
        User,
        verbose_name=_("Created by"),
        related_name="plugins_created_by",
        on_delete=models.CASCADE,
    )

    # maintainer
    maintainer = models.ForeignKey(
        User,
        verbose_name=_("Maintainer"),
        related_name="plugins_maintainer",
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )

    display_created_by = models.BooleanField(
        _('Display "Created by" in plugin details'),
        default=False
    )

    author = models.CharField(
        _("Author"),
        help_text=_(
            "This is the plugin's original author, if different from the uploader, this field will appear in the XML and in the web GUI"
        ),
        max_length=256,
    )
    email = models.EmailField(_("Author email"))
    homepage = models.URLField(_("Plugin homepage"), blank=True, null=True)
    # Support
    repository = models.URLField(_("Code repository"), blank=False, null=True)
    tracker = models.URLField(_("Tracker"), blank=False, null=True)

    owners = models.ManyToManyField(User, blank=True)

    # name, desc etc.
    package_name = models.CharField(
        _("Package Name"),
        help_text=_(
            "This is the plugin's internal name, equals to the main folder name"
        ),
        max_length=256,
        unique=True,
        editable=False,
    )
    name = models.CharField(
        _("Name"), help_text=_("Must be unique"), max_length=256, unique=True
    )

    allow_update_name = models.BooleanField(
        _("Allow update name"), 
        help_text=_("Allow name in metadata.txt to update the plugin name"), 
        default=False
    )

    description = models.TextField(_("Description"))
    about = models.TextField(_("About"), blank=False, null=True)

    icon = models.ImageField(
        _("Icon"), blank=True, null=True, upload_to=PLUGINS_STORAGE_PATH
    )

    # downloads (soft trigger from versions)
    downloads = models.IntegerField(_("Downloads"), default=0, editable=False)

    # Flags
    featured = models.BooleanField(_("Featured"), default=False, db_index=True)
    deprecated = models.BooleanField(_("Deprecated"), default=False, db_index=True)

    # True if the plugin has a server interface
    server = models.BooleanField(_("Server"), default=False, db_index=True)

    # Managers
    objects = models.Manager()
    base_objects = BasePluginManager()
    approved_objects = ApprovedPlugins()
    stable_objects = StablePlugins()
    experimental_objects = ExperimentalPlugins()
    featured_objects = FeaturedPlugins()
    fresh_objects = FreshPlugins()
    latest_objects = LatestPlugins()
    unapproved_objects = UnapprovedPlugins()
    deprecated_objects = DeprecatedPlugins()
    popular_objects = PopularPlugins()
    most_downloaded_objects = MostDownloadedPlugins()
    most_voted_objects = MostVotedPlugins()
    most_rated_objects = MostRatedPlugins()
    server_objects = ServerPlugins()
    feedback_received_objects = FeedbackReceivedPlugins()
    feedback_pending_objects = FeedbackPendingPlugins()

    rating = AnonymousRatingField(
        range=5, use_cookies=True, can_change_vote=True, allow_delete=True
    )

    tags = TaggableManager(blank=True)

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
        return self.created_by.has_perm("plugins.can_approve")

    @property
    def stable(self):
        """
        Returns the latest stable and approved version
        """
        try:
            return self.pluginversion_set.filter(
                approved=True, experimental=False
            ).order_by("-version")[0]
        except:
            return None

    @property
    def experimental(self):
        """
        Returns the latest experimental and approved version
        """
        try:
            return self.pluginversion_set.filter(
                approved=True, experimental=True
            ).order_by("-version")[0]
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
        return [l for l in self.editors if l.has_perm("plugins.can_approve")]

    @property
    def avg_vote(self):
        """
        Returns the rating_score/(rating_votes+0.001) value, this
        calculation is also available in manager's queries as
        "average_vote".
        This property is still useful when the object is not loaded
        through a manager, for example in related objects.
        """
        return self.rating_score / (self.rating_votes + 0.001)

    class Meta:
        ordering = ("name",)
        # ABP: Note: this permission should belong to the
        # PluginVersion class. I left it here because it
        # doesn't really matters where it is. Just be
        # sure you query for it using the 'plugins' class
        # instead of the 'pluginversion' class.
        permissions = (("can_approve", "Can approve plugins versions"),)

    def get_absolute_url(self):
        return reverse("plugin_detail", args=(self.package_name,))

    def __unicode__(self):
        return "[%s] %s" % (self.pk, self.name)

    def __str__(self):
        return self.__unicode__()

    def clean(self):
        """
        Validates:

        * Checks that package_name respect regexp [A-Za-z][A-Za-z0-9-_]+
        * checks for case-insensitive unique package_name
        """
        from django.core.exceptions import ValidationError

        if not re.match(r"^[A-Za-z][A-Za-z0-9-_]+$", self.package_name):
            raise ValidationError(
                _(
                    "Plugin package_name (which equals to the main plugin folder inside the zip file) must start with an ASCII letter and can contain only ASCII letters, digits and the - and _ signs."
                )
            )

        if self.pk:
            qs = Plugin.objects.filter(name__iexact=self.name).exclude(pk=self.pk)
        else:
            qs = Plugin.objects.filter(name__iexact=self.name)
        if qs.count():
            raise ValidationError(
                _(
                    "A plugin with a similar name (%s) already exists (the name only differs in case)."
                )
                % qs.all()[0].name
            )

        if self.pk:
            qs = Plugin.objects.filter(package_name__iexact=self.package_name).exclude(
                pk=self.pk
            )
        else:
            qs = Plugin.objects.filter(package_name__iexact=self.package_name)
        if qs.count():
            raise ValidationError(
                _(
                    "A plugin with a similar package_name (%s) already exists (the package_name only differs in case)."
                )
                % qs.all()[0].package_name
            )

    def save(self, keep_date=False, *args, **kwargs):
        """
        Soft triggers:
        * updates modified_on if keep_date is not set
        * set maintainer to the plugin creator when not specified
        """
        if self.pk and not keep_date:
            import logging

            logging.debug("Updating modified_on for the Plugin instance")
            self.modified_on = datetime.datetime.now()
        if not self.pk:
            self.modified_on = datetime.datetime.now()
        if not self.maintainer:
            self.maintainer = self.created_by
        super(Plugin, self).save(*args, **kwargs)


# Plugin version managers


class ApprovedPluginVersions(models.Manager):
    """
    Shows only public plugin versions:
    """

    def get_queryset(self):
        return (
            super(ApprovedPluginVersions, self)
            .get_queryset()
            .filter(approved=True)
            .order_by("-version")
        )


class StablePluginVersions(ApprovedPluginVersions):
    """
    Shows only approved public plugin versions: i.e. those with "approved" flag set
    and with "stable" flag
    """

    def get_queryset(self):
        return (
            super(StablePluginVersions, self).get_queryset().filter(experimental=False)
        )


class ExperimentalPluginVersions(ApprovedPluginVersions):
    """
    Shows only public plugin versions: i.e. those with "approved" flag set
    and with  "experimental" flag
    """

    def get_queryset(self):
        return (
            super(ExperimentalPluginVersions, self)
            .get_queryset()
            .filter(experimental=True)
        )


def vjust(str, level=3, delim=".", bitsize=3, fillchar=" ", force_zero=False):
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
            str += (level - nb) * (delim + "0")
        else:
            str += (level - nb) * delim
    parts = []
    for v in str.split(delim)[: level + 1]:
        if not v:
            parts.append(v.rjust(bitsize, "#"))
        else:
            parts.append(v.rjust(bitsize, fillchar))
    return delim.join(parts)


class VersionField(models.CharField):

    description = 'Field to store version strings ("a.b.c.d") in a way it is sortable'

    def get_prep_value(self, value):
        return vjust(value, fillchar="0")

    def to_python(self, value):
        if not value:
            return ""
        return re.sub(VERSION_RE, "", value)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.to_python(value)


class QGVersionZeroForcedField(models.CharField):

    description = 'Field to store version strings ("a.b.c.d") in a way it \
    is sortable and QGIS scheme compatible (x.y.z).'

    def get_prep_value(self, value):
        return vjust(value, fillchar="0", level=2, force_zero=True)

    def to_python(self, value):
        if not value:
            return ""
        return re.sub(VERSION_RE, "", value)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return self.to_python(value)


class PluginOutstandingToken(models.Model):
    """
    Plugin outstanding token
    """
    plugin = models.ForeignKey(
        Plugin,
        on_delete=models.CASCADE
    )
    token = models.ForeignKey(
        OutstandingToken,
        on_delete=models.CASCADE
    )
    is_blacklisted = models.BooleanField(default=False)
    is_newly_created = models.BooleanField(default=False)
    description = models.CharField(
        verbose_name=_("Description"),
        help_text=_("Describe this token so that it's easier to remember where you're using it."),
        max_length=512,
        blank=True,
        null=True,
    )
    last_used_on = models.DateTimeField(
        verbose_name=_("Last used on"),
        blank=True,
        null=True
    )

class PluginVersion(models.Model):
    """
    Plugin versions
    """

    # link to parent
    plugin = models.ForeignKey(Plugin, on_delete=models.CASCADE)
    # dates
    created_on = models.DateTimeField(
        _("Created on"), auto_now_add=True, editable=False
    )
    # download counter
    downloads = models.IntegerField(_("Downloads"), default=0, editable=False)
    # owners
    created_by = models.ForeignKey(
        User, verbose_name=_("Created by"), on_delete=models.CASCADE, null=True, blank=True
    )
    # version info, the first should be read from plugin
    min_qg_version = QGVersionZeroForcedField(
        _("Minimum QGIS version"), max_length=32, db_index=True
    )
    max_qg_version = QGVersionZeroForcedField(
        _("Maximum QGIS version"), max_length=32, null=True, blank=True, db_index=True
    )
    version = VersionField(_("Version"), max_length=32, db_index=True)
    changelog = models.TextField(_("Changelog"), null=True, blank=True)

    # the file!
    package = models.FileField(_("Plugin package"), upload_to=PLUGINS_STORAGE_PATH)
    # Flags: checks on unique current/experimental are done in save() and possibly in the views
    experimental = models.BooleanField(
        _("Experimental flag"),
        default=False,
        help_text=_(
            "Check this box if this version is experimental, leave unchecked if it's stable. Please note that this field might be overridden by metadata (if present)."
        ),
        db_index=True,
    )
    approved = models.BooleanField(
        _("Approved"),
        default=True,
        help_text=_("Set to false if you wish to unapprove the plugin version."),
        db_index=True,
    )
    external_deps = models.CharField(
        _("External dependencies"),
        help_text=_("PIP install string"),
        max_length=512,
        blank=False,
        null=True,
    )
    is_from_token = models.BooleanField(
        _("Is uploaded using token"),
        default=False
    )
    # Link to the token if upload is using token
    token = models.ForeignKey(
        PluginOutstandingToken, verbose_name=_("Token used"), on_delete=models.CASCADE, null=True, blank=True
    )

    # Managers, used in xml output
    objects = models.Manager()
    approved_objects = ApprovedPluginVersions()
    stable_objects = StablePluginVersions()
    experimental_objects = ExperimentalPluginVersions()

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
        if self.version.rfind(" ") > 0:
            self.version = self.version.rsplit(" ")[-1]

        # Only change modified_on when a new version is created,
        # every download triggers a save to update the counter
        if not self.pk:
            self.plugin.modified_on = self.created_on
            self.plugin.save()

        # fix Max version
        if not self.max_qg_version:
            self.max_qg_version = "%s.99" % tuple(self.min_qg_version.split(".")[0])

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

        versions_to_check = PluginVersion.objects.filter(
            plugin=self.plugin, version=self.version
        )
        if self.pk:
            versions_to_check = versions_to_check.exclude(pk=self.pk)
        # Checks for unique_together
        if (
            versions_to_check.filter(plugin=self.plugin, version=self.version).count()
            > 0
        ):
            raise ValidationError(
                _(
                    "Version value must be unique among each plugin: a version with same number already exists."
                )
            )

    @staticmethod
    def clean_version(version):
        """
        Strips blanks and Version string
        """
        if version.rfind(" ") > 0:
            version = version.rsplit(" ")[-1]
        return version

    class Meta:
        unique_together = ("plugin", "version")
        ordering = ("plugin", "-version", "experimental")

    def get_absolute_url(self):
        return reverse(
            "version_detail",
            args=(
                self.plugin.package_name,
                self.version,
            ),
        )

    def get_download_url(self):
        return reverse(
            "version_download",
            args=(
                self.plugin.package_name,
                self.version,
            ),
        )

    def download_file_name(self):
        return "%s.%s.zip" % (self.plugin.package_name, self.version)

    def __unicode__(self):
        desc = "%s %s" % (self.plugin, self.version)
        if self.experimental:
            desc = "%s %s" % (desc, _("Experimental"))
        return desc

    def __str__(self):
        return self.__unicode__()


class PluginVersionFeedback(models.Model):
    """Feedback for a plugin version."""

    version = models.ForeignKey(
        PluginVersion,
        on_delete=models.CASCADE,
        related_name="feedback"
    )
    reviewer = models.ForeignKey(
        User,
        verbose_name=_("Reviewed by"),
        help_text=_("The user who reviewed this plugin."),
        on_delete=models.CASCADE,
    )
    task = models.TextField(
        verbose_name=_("Task"),
        help_text=_("A feedback task. Please write your review as a task for this plugin."),
        max_length=1000,
        blank=False,
        null=False
    )
    created_on = models.DateTimeField(
        verbose_name=_("Created on"),
        auto_now_add=True,
        editable=False
    )
    completed_on = models.DateTimeField(
        verbose_name=_("Completed on"),
        blank=True,
        null=True
    )
    is_completed = models.BooleanField(
        verbose_name=_("Completed"),
        default=False,
        db_index=True
    )

    class Meta:
        ordering = ["created_on"]

    def save(self, *args, **kwargs):
        if self.is_completed is True:
            self.completed_on = datetime.datetime.now()
        else:
            self.completed_on = None
        super(PluginVersionFeedback, self).save(*args, **kwargs)


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


class PluginVersionDownload(models.Model):
    """
    Plugin version downloads
    """
    plugin_version = models.ForeignKey(
        PluginVersion, 
        on_delete=models.CASCADE
    )
    download_date = models.DateField(
        default=timezone.now
    )
    country_code = models.CharField(max_length=3, default='N/D')
    country_name = models.CharField(max_length=100, default='N/D')
    download_count = models.IntegerField(
        default=0
    )
    class Meta:
        unique_together = (
            'plugin_version',
            'download_date'
        )


models.signals.post_delete.connect(delete_version_package, sender=PluginVersion)
models.signals.post_delete.connect(delete_plugin_icon, sender=Plugin)
