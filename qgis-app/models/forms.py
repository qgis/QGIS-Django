from django.utils.translation import ugettext_lazy as _
from django import forms

from models.models import Model
from models.validator import model_validator


class ModelUploadForm(forms.ModelForm):
    """
    Model Upload Form.
    """

    class Meta:
        model = Model
        fields = ['model_file', 'thumbnail_image', 'name', 'description', ]

    def clean_model_file(self):
        """
        Cleaning model_file field data.
        """

        model_file = self.cleaned_data['model_file']
        if model_validator(model_file.file):
            return model_file


class ModelUpdateForm(ModelUploadForm):
    """
    Model Update Form.
    """

    class Meta:
        model = Model
        fields = ['name', 'model_file', 'thumbnail_image', 'description', ]


class ModelReviewForm(forms.Form):
    """
    Model Review Form.
    """

    CHOICES = [('approve', 'Approve'), ('reject', 'Reject')]
    approval = forms.ChoiceField(required=True, choices=CHOICES,
                                 widget=forms.RadioSelect, initial='approve')
    comment = forms.CharField(widget=forms.Textarea(
        attrs={'placeholder': _('Please provide clear feedback if you decided '
                                'to not approve this Model.'),
               'rows': "5"}))


class ModelSearchForm(forms.Form):
    """
    Search Form
    """

    q = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'search-query', 'placeholder': 'Search'}))
