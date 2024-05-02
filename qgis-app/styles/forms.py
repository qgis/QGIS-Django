from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from styles.file_handler import validator
from styles.models import Style


class ResourceFormMixin(forms.ModelForm):
    class Meta:
        model = Style
        fields = [
            "file",
            "thumbnail_image",
            "name",
            "description",
        ]


class UploadForm(forms.ModelForm):
    """
    Style Upload Form.
    """

    class Meta:
        model = Style
        fields = [
            "file",
            "thumbnail_image",
            "description",
        ]

    def clean_file(self):
        """
        Cleaning file field data.
        """

        xml_file = self.cleaned_data["file"]

        if xml_file:
            style = validator(xml_file.file)
            if not style:
                raise ValidationError(
                    _("Undefined style type. " "Please register your style type.")
                )
        return xml_file


class UpdateForm(ResourceFormMixin):
    """Style Update Form."""


class StyleReviewForm(forms.Form):
    """
    Style Review Form.
    """

    CHOICES = [("approve", "Approve"), ("reject", "Reject")]
    approval = forms.ChoiceField(
        required=True, choices=CHOICES, widget=forms.RadioSelect, initial="approve"
    )
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "placeholder": "Please provide clear feedback "
                "if you decided to not approve this style.",
                "rows": "5",
            }
        )
    )


class StyleSearchForm(forms.Form):
    """
    Search Form
    """

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "search-query", "placeholder": "Search"}
        ),
    )
