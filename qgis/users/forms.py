from users.models import *
from django import forms

class QgisUserForm(forms.ModelForm):
  class Meta:
    model = QgisUser


