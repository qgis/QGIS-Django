from base.forms.processing_forms import ResourceBaseCleanFileForm
from django import forms
from models.models import Model


class ResourceFormMixin(forms.ModelForm):
    class Meta:
        model = Model
        fields = [
            "file",
            "thumbnail_image",
            "name",
            "description",
        ]


class UploadForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Upload Form."""


class UpdateForm(ResourceFormMixin):
    """Model Update Form."""
