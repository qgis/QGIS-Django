from django.utils.translation import ugettext_lazy as _
from django import forms
from django.core.exceptions import ValidationError

from geopackages.models import Geopackage
from geopackages.validator import gpkg_validator


class GeopackageUploadForm(forms.ModelForm):
    """
    GeoPackage Upload Form.
    """

    class Meta:
        model = Geopackage
        fields = ['gpkg_file', 'thumbnail_image', 'name','description', ]

    def clean_gpkg_file(self):
        """
        Cleaning gpkg_file field data.
        """

        gpkg_file = self.cleaned_data['gpkg_file']
        if gpkg_validator(gpkg_file.file):
            return gpkg_file


class GeopackageUpdateForm(GeopackageUploadForm):
    """
    GeoPackage Update Form.
    """

    class Meta:
        model = Geopackage
        fields = ['name', 'gpkg_file', 'thumbnail_image', 'description', ]


class GeopackageReviewForm(forms.Form):
    """
    GeoPackage Review Form.
    """

    CHOICES = [('approve', 'Approve'), ('reject', 'Reject')]
    approval = forms.ChoiceField(required=True, choices=CHOICES,
                                 widget=forms.RadioSelect, initial='approve')
    comment = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': 'Please provide clear feedback '
                              'if you decided to not approve this GeoPackage.',
               'rows': "5"}))


class GeopackageSearchForm(forms.Form):
    """
    Search Form
    """

    q = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'search-query', 'placeholder': 'Search'}))
