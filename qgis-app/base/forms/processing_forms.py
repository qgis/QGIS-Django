from django import forms
from django.utils.translation import ugettext_lazy as _

from geopackages.validator import gpkg_validator


class ResourceBaseReviewForm(forms.Form):
    """Base Review Form for sharing file app."""

    CHOICES = [('approve', 'Approve'), ('reject', 'Reject')]
    approval = forms.ChoiceField(required=True, choices=CHOICES,
                                 widget=forms.RadioSelect, initial='approve')
    comment = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': _('Please provide clear feedback if you decided '
                                'to not approve this GeoPackage.'),
               'rows': "5"}))


class ResourceBaseSearchForm(forms.Form):
    """Base Search Form for sharing file app."""
    q = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'search-query', 'placeholder': 'Search'}))


class ResourceBaseCleanFileForm(object):
    def clean_gpkg_file(self):
        """
        Cleaning gpkg_file field data.
        """

        gpkg_file = self.cleaned_data['gpkg_file']
        if gpkg_validator(gpkg_file.file):
            return gpkg_file