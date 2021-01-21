from django import forms

from geopackages.models import Geopackage

from base.forms.processing_forms import (ResourceBaseReviewForm,
                                         ResourceBaseSearchForm,
                                         ResourceBaseCleanFileForm)


class ResourceFormMixin(forms.ModelForm):
    class Meta:
        model = Geopackage
        fields = ['file', 'thumbnail_image', 'name', 'description', ]


class UploadForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Upload Form."""

    pass


class UpdateForm(ResourceFormMixin):
    """GeoPackage Update Form."""

    pass


class GeopackageReviewForm(ResourceBaseReviewForm):
    """GeoPackage Review Form."""

    pass


class GeopackageSearchForm(ResourceBaseSearchForm):
    """Search Form"""

    pass
