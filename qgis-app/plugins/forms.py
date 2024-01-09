# i18n
import re

from django import forms
from django.contrib.auth.models import User
from django.forms import CharField, ModelForm, ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from plugins.models import Plugin, PluginOutstandingToken, PluginVersion, PluginVersionFeedback
from plugins.validator import validator
from taggit.forms import *


def _clean_tags(tags):
    """Return a stripped and cleaned tag list, empty tags are deleted"""
    if tags:
        _tags = []
        for t in tags.split(","):
            if t.strip():
                _tags.append(t.strip())
        return ",".join(_tags)
    return None


class PluginForm(ModelForm):
    """
    Form for plugin editing
    """

    required_css_class = "required"
    tags = TagField(required=False)

    class Meta:
        model = Plugin
        fields = (
            "description",
            "about",
            "author",
            "email",
            "icon",
            "deprecated",
            "homepage",
            "tracker",
            "repository",
            "owners",
            "maintainer",
            "display_created_by",
            "tags",
            "server",
        )

    def __init__(self, *args, **kwargs):
        super(PluginForm, self).__init__(*args, **kwargs)
        self.fields['owners'].label = "Collaborators"

        choices = (
            (self.instance.created_by.pk, self.instance.created_by.username + " (Plugin creator)"),
        )
        for owner in self.instance.owners.exclude(pk=self.instance.created_by.pk):
            choices += ((owner.pk, owner.username + " (Collaborator)"),)

        self.fields['maintainer'].choices = choices
        self.fields['maintainer'].label = "Maintainer"

    def clean(self):
        """
        Check author
        """
        if self.cleaned_data.get("author") and not re.match(
            r"^[^/]+$", self.cleaned_data.get("author")
        ):
            raise ValidationError(_("Author name cannot contain slashes."))
        return super(PluginForm, self).clean()


class PluginVersionForm(ModelForm):
    """
    Form for version upload on existing plugins
    """

    required_css_class = "required"
    changelog = forms.fields.CharField(
        label=_("Changelog"),
        required=False,
        help_text=_(
            "Insert here a short description of the changes that have been made in this version. This field is not mandatory and it is automatically filled from the metadata.txt file."
        ),
        widget=forms.Textarea,
    )

    def __init__(self, *args, **kwargs):
        kwargs.pop("is_trusted")
        super(PluginVersionForm, self).__init__(*args, **kwargs)
        # FIXME: check why this is not working correctly anymore
        #        now "approved" is removed from the form (see Meta)
        # instance = getattr(self, 'instance', None)
        # if instance and not is_trusted:
        #    self.fields['approved'].initial = False
        #    self.fields['approved'].widget.attrs = {'disabled':'disabled'}
        #    instance.approved = False

    class Meta:
        model = PluginVersion
        exclude = (
            "created_by",
            "plugin",
            "approved",
            "version",
            "min_qg_version",
            "max_qg_version",
        )
        fields = ("package", "experimental", "changelog")

    def clean(self):
        """
        Only read package if uploaded
        """
        # Override package
        changelog = self.cleaned_data.get("changelog")

        if self.files:
            package = self.cleaned_data.get("package")
            try:
                cleaned_data = validator(package)
                if (
                    "experimental" in dict(cleaned_data)
                    and "experimental" in self.cleaned_data
                    and dict(cleaned_data)["experimental"]
                    != self.cleaned_data["experimental"]
                ):
                    msg = _(
                        "The 'experimental' flag in the form does not match the 'experimental' flag in the plugins package metadata.<br />"
                    )
                    raise ValidationError(mark_safe("%s" % msg))
                self.cleaned_data.update(cleaned_data)
            except ValidationError as e:
                msg = _(
                    "There were errors reading plugin package (please check also your plugin's metadata).<br />"
                )
                raise ValidationError(
                    mark_safe("%s %s" % (msg, "<br />".join(e.messages)))
                )
            # Populate instance
            self.instance.min_qg_version = self.cleaned_data.get("qgisMinimumVersion")
            self.instance.max_qg_version = self.cleaned_data.get("qgisMaximumVersion")
            self.instance.version = PluginVersion.clean_version(
                self.cleaned_data.get("version")
            )
            self.instance.server = self.cleaned_data.get("server")

            # Check plugin folder name 
            if (
                self.cleaned_data.get("package_name")
                and self.cleaned_data.get("package_name")
                != self.instance.plugin.package_name
            ):
                raise ValidationError(
                    _(
                        "Plugin folder name mismatch: the plugin main folder name in the compressed file (%s) is different from the original plugin package name (%s)."
                    )
                    % (
                        self.cleaned_data.get("package_name"),
                        self.instance.plugin.package_name,
                    )
                )
        # Also set changelog from metadata
        if changelog:
            self.cleaned_data["changelog"] = changelog
        # Clean tags
        self.cleaned_data["tags"] = _clean_tags(self.cleaned_data.get("tags", None))
        self.instance.changelog = self.cleaned_data.get("changelog")
        return super(PluginVersionForm, self).clean()


class PackageUploadForm(forms.Form):
    """
    Single step upload for new plugins
    """

    experimental = forms.BooleanField(
        required=False,
        label=_("Experimental"),
        help_text=_(
            "Please check this box if the plugin is experimental. Please note that this field might be overridden by metadata (if present)."
        ),
    )
    package = forms.FileField(
        label=_("Plugin package"),
        help_text=_("Please select the zipped file of the plugin."),
    )

    def clean_package(self):
        """
        Populates cleaned_data with metadata from the zip package
        """
        package = self.cleaned_data.get("package")
        try:
            self.cleaned_data.update(validator(package))
        except ValidationError as e:
            msg = _(
                "There were errors reading plugin package (please check also your plugin's metadata)."
            )
            raise ValidationError(mark_safe("%s %s" % (msg, ",".join(e.messages))))
        # Disabled: now the PackageUploadForm also accepts updates
        # if Plugin.objects.filter(package_name = self.cleaned_data['package_name']).count():
        #    raise ValidationError(_('A plugin with this package name (%s) already exists. To update an existing plugin, you should open the plugin\'s details view and add a new version from there.') % self.cleaned_data['package_name'])

        # if Plugin.objects.filter(name = self.cleaned_data['name']).count():
        #    raise ValidationError(_('A plugin with this name (%s) already exists.') % self.cleaned_data['name'])
        self.cleaned_data["version"] = PluginVersion.clean_version(
            self.cleaned_data["version"]
        )
        # Checks for version
        if Plugin.objects.filter(
            package_name=self.cleaned_data["package_name"],
            pluginversion__version=self.cleaned_data["version"],
        ).count():
            raise ValidationError(
                _(
                    "A plugin with this name (%s) and version number (%s) already exists."
                )
                % (self.cleaned_data["name"], self.cleaned_data["version"])
            )
        # Clean tags
        self.cleaned_data["tags"] = _clean_tags(self.cleaned_data.get("tags", None))
        return package


class VersionFeedbackForm(forms.Form):
    """Feedback for a plugin version"""

    feedback = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": _(
                    "Please provide clear feedback as a task. \n"
                    "You can create multiple tasks with '- [ ]'.\n"
                    "e.g:\n"
                    "- [ ] first task\n"
                    "- [ ] second task"
                ),
                "rows": "5",
                "class": "span12"
            }
        )
    )

    def clean(self):
        super().clean()
        feedback = self.cleaned_data.get('feedback')

        if feedback:
            lines: list = feedback.split('\n')
            bullet_points: list = [
                line[6:].strip() for line in lines if line.strip().startswith('- [ ]')
            ]
            has_bullet_point = len(bullet_points) >= 1
            tasks: list = bullet_points if has_bullet_point else [feedback]
            self.cleaned_data['tasks'] = tasks

        return self.cleaned_data

class PluginTokenForm(ModelForm):
    """
    Form for token description editing
    """

    class Meta:
        model = PluginOutstandingToken
        fields = (
            "description",
        )