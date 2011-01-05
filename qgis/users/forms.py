from users.models import *
from django import forms
from django.forms import ModelForm, Textarea, TextInput


class QgisUserForm(forms.ModelForm):
  name = forms.CharField(label="Name:",
               required=True,
               widget=forms.TextInput(attrs={'size': 50,}),
               help_text="",
               error_messages={'required': 
               '''Please enter the name of the user'''},
              )

  class Meta:
    model = QgisUser
    exclude = ('added_date', 'guid',)
    widgets = {
            'email': TextInput(attrs={'size': 50,}),
            'home_url': TextInput(attrs={'size': 50,}),                        
        }



