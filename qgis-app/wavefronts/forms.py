from django import forms

from wavefronts.models import Wavefront

from base.forms.processing_forms import ResourceBaseCleanFileForm


class ResourceFormMixin(forms.ModelForm):
    class Meta:
        model = Wavefront
        fields = ['file', 'thumbnail_image', 'name', 'description', ]


class UploadForm(ResourceBaseCleanFileForm, ResourceFormMixin):
    """Upload Form."""


class UpdateForm(ResourceFormMixin):
    """Model Update Form."""
