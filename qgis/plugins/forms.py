# i18n
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.forms import ModelForm, ValidationError
from django import forms

from plugins.validator import validator
from plugins.models import *


class PluginForm(ModelForm):
    """
    Form for plugin editing
    """

    class Meta:
        model = Plugin
        fields = ('description', 'homepage', 'owners')


class PluginVersionForm(ModelForm):
    """
    Form for version upload on existing plugins
    """
    class Meta:
        model = PluginVersion
        exclude = ('created_by', 'plugin', 'version', 'min_qg_version')

    def clean_package(self):
        package         = self.cleaned_data.get('package')
        try:
            self.cleaned_data.update(validator(package))
        except ValidationError, e:
            msg = unicode(_('File upload must be a valid QGIS Python plugin compressed archive.'))
            raise ValidationError("%s %s" % (msg, ','.join(e.messages)))

        return package

    def clean(self):
        # Populate instance
        self.instance.min_qg_version = self.cleaned_data.get('qgisMinimumVersion')
        self.instance.version        = self.cleaned_data.get('version')
        # Check plugin name
        if self.cleaned_data.get('package_name') and self.cleaned_data.get('package_name') != self.instance.plugin.package_name:
            raise ValidationError(_('Plugin name mismatch: the plugin main folder name in the compressed file is different from the original plugin package name.'))
        return super(PluginVersionForm, self).clean()


class PackageUploadForm(forms.Form):
    """
    Single step upload for new plugins
    """
    package = forms.FileField(_('QGIS compressed plugin package'))
    experimental = forms.BooleanField(required = False, label = _('Experimental'))

    def clean_package(self):
        cleaned_data    = self.cleaned_data
        package         = self.cleaned_data.get('package')
        try:
            self.cleaned_data.update(validator(package))
        except ValidationError, e:
            msg = unicode(_('File upload must be a valid QGIS Python plugin compressed archive.'))
            raise ValidationError("%s %s" % (msg, ','.join(e.messages)))

        if Plugin.objects.filter(name = self.cleaned_data['package_name']).count():
            raise ValidationError(_('A plugin with this package name (%s) already exists.') % self.cleaned_data['package_name'])

        if Plugin.objects.filter(name = self.cleaned_data['name']).count():
            import ipy; ipy.shell()
            raise ValidationError(_('A plugin with this name (%s) already exists.') % self.cleaned_data['name'])
        return package

