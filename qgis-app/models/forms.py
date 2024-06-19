from base.forms.processing_forms import ResourceBaseCleanFileForm
from django import forms
from models.models import Model
from taggit.forms import TagField


class ResourceFormMixin(forms.ModelForm):
    tags = TagField(required=False)
    class Meta:
        model = Model
        fields = [
            "file",
            "thumbnail_image",
            "name",
            "description",
            "tags"
        ]


class UploadForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Upload Form."""


class UpdateForm(ResourceFormMixin):
    """Model Update Form."""
