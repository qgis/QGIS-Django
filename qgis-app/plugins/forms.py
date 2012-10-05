# i18n
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.forms import ModelForm, ValidationError
from django import forms

from plugins.validator import validator
from plugins.models import *
from taggit.forms import *

import re

class PluginForm(ModelForm):
    """
    Form for plugin editing
    """

    tags = TagField(required=False)

    class Meta:
        model = Plugin
        fields = ('description', 'author', 'email', 'icon', 'deprecated', 'homepage', 'tracker', 'repository', 'owners', 'tags')


class PluginVersionForm(ModelForm):
    """
    Form for version upload on existing plugins
    """
    changelog = forms.fields.CharField(label=_('Changelog'), required=False,
                help_text=_('Insert here a short description of the changes that have been made in this version. This field is not mandatory and can be automatically read from the metadata.txt file.'), widget=forms.Textarea)


    def __init__(self, *args, **kwargs):
        is_trusted = kwargs.pop('is_trusted')
        super(PluginVersionForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and not is_trusted:
            self.fields['approved'].initial = False
            self.fields['approved'].widget.attrs = {'disabled':'disabled'}
            instance.approved = False


    class Meta:
        model = PluginVersion
        exclude = ('created_by', 'plugin', 'version', 'min_qg_version')
        fields = ('package', 'experimental', 'approved', 'changelog')

    def clean(self):
        """
        Only read package if uploaded
        """

        # Override package
        changelog = self.cleaned_data.get('changelog')

        if self.files:
            package         = self.cleaned_data.get('package')
            try:
                self.cleaned_data.update(validator(package))
            except ValidationError, e:
                msg = unicode(_("There were errors reading plugin package (please check also your plugin's metadata)."))
                raise ValidationError("%s %s" % (msg, ','.join(e.messages)))
            # Populate instance
            self.instance.min_qg_version = self.cleaned_data.get('qgisMinimumVersion')
            self.instance.version        = PluginVersion.clean_version(self.cleaned_data.get('version'))
            # Check plugin name
            if self.cleaned_data.get('package_name') and self.cleaned_data.get('package_name') != self.instance.plugin.package_name:
                raise ValidationError(_('Plugin name mismatch: the plugin main folder name in the compressed file (%s) is different from the original plugin package name (%s).') % (self.cleaned_data.get('package_name'), self.instance.plugin.package_name))

        # Also set changelog from metadata
        if changelog:
            self.cleaned_data['changelog'] = changelog

        self.instance.changelog = self.cleaned_data.get('changelog')
        

        return super(PluginVersionForm, self).clean()


class PackageUploadForm(forms.Form):
    """
    Single step upload for new plugins
    """
    experimental = forms.BooleanField(required=False, label=_('Experimental'), help_text=_('Please check this box if the plugin is experimental. Please note that this field might be overridden by metadata (if present).'))
    package = forms.FileField(_('QGIS compressed plugin package'), label=_('Plugin package'), help_text=_('Please select the zipped file of the plugin.'))

    def clean_package(self):
        """
        Populates cleaned_data with metadata from the zip package
        """
        package         = self.cleaned_data.get('package')
        try:
            self.cleaned_data.update(validator(package))
        except ValidationError, e:
            msg = unicode(_("There were errors reading plugin package (please check also your plugin's metadata)."))
            raise ValidationError("%s %s" % (msg, ','.join(e.messages)))

        # Disabled: now the PackageUploadForm also accepts updates
        #if Plugin.objects.filter(package_name = self.cleaned_data['package_name']).count():
        #    raise ValidationError(_('A plugin with this package name (%s) already exists. To update an existing plugin, you should open the plugin\'s details view and add a new version from there.') % self.cleaned_data['package_name'])

        #if Plugin.objects.filter(name = self.cleaned_data['name']).count():
        #    raise ValidationError(_('A plugin with this name (%s) already exists.') % self.cleaned_data['name'])

        self.cleaned_data['version'] = PluginVersion.clean_version(self.cleaned_data['version'])

        # Checks for version
        if Plugin.objects.filter(package_name=self.cleaned_data['package_name'], pluginversion__version=self.cleaned_data['version']).count():
            raise ValidationError(_('A plugin with this name (%s) and version number (%s) already exists.') % (self.cleaned_data['name'], self.cleaned_data['version']))

        return package

