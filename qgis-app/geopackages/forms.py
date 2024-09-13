from base.forms.processing_forms import ResourceBaseCleanFileForm
from django import forms
from geopackages.models import Geopackage
from taggit.forms import TagField


class ResourceFormMixin(forms.ModelForm):
    tags = TagField(required=False)
    class Meta:
        model = Geopackage
        fields = [
            "file",
            "thumbnail_image",
            "name",
            "description",
            "tags",
        ]


class UploadForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Upload Form."""


class UpdateForm(ResourceFormMixin):
    """GeoPackage Update Form."""
