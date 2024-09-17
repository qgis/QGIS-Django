from django.forms import CharField, ModelForm
from api.models import UserOutstandingToken


class UserTokenForm(ModelForm):
    """
    Form for token description editing
    """

    class Meta:
        model = UserOutstandingToken
        fields = (
            "description",
        )