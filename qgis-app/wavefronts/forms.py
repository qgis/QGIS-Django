from django import forms

from wavefronts.models import Wavefront
from wavefronts.validator import WavefrontValidator

from base.forms.processing_forms import ResourceBaseCleanFileForm


class ResourceFormMixin(forms.ModelForm):
    class Meta:
        model = Wavefront
        fields = ['file', 'thumbnail_image', 'name', 'description', ]


class UploadForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Upload Form."""

    def clean_file(self):
        zip_file = self.cleaned_data['file']
        if zip_file:
            WavefrontValidator(zip_file).validate_wavefront()
        return zip_file



class UpdateForm(ResourceFormMixin):
    """Model Update Form."""
