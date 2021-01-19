from django import forms

from geopackages.models import Geopackage

from base.forms.processing_forms import (ResourceBaseReviewForm,
                                         ResourceBaseSearchForm,
                                         ResourceBaseCleanFileForm)


class GeopackageFormMixin(forms.ModelForm):
    class Meta:
        model = Geopackage
        fields = ['gpkg_file', 'thumbnail_image', 'name', 'description', ]


class GeopackageUploadForm(ResourceBaseCleanFileForm, GeopackageFormMixin):
    """GeoPackage Upload Form."""

    pass


class GeopackageUpdateForm(GeopackageFormMixin):
    """GeoPackage Update Form."""

    pass


class GeopackageReviewForm(ResourceBaseReviewForm):
    """GeoPackage Review Form."""

    pass


class GeopackageSearchForm(ResourceBaseSearchForm):
    """Search Form"""

    pass
