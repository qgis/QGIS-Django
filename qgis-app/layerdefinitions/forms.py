from base.forms.processing_forms import ResourceBaseCleanFileForm
from django import forms
from layerdefinitions.file_handler import validator
from layerdefinitions.models import LayerDefinition
from taggit.forms import TagField


class ResourceFormMixin(forms.ModelForm):
    tags = TagField(required=False)
    class Meta:
        model = LayerDefinition
        fields = [
            "file",
            "thumbnail_image",
            "name",
            "url_metadata",
            "description",
            "license",
            "tags"
        ]


class UploadForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Upload Form."""

    def clean_file(self):
        file = super(UploadForm, self).clean_file()
        validator(file)
        return file


class UpdateForm(ResourceFormMixin):
    """Update Form."""
