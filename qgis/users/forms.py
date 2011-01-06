from users.models import *
from django import forms
from django.conf import settings
from django.forms import ModelForm, Textarea, TextInput

from olwidget.widgets import EditableMap
from olwidget.forms import MapModelForm
from olwidget.fields import MapField, EditableLayerField, InfoLayerField

from users.models import QgisUser

class QgisUserForm(MapModelForm):
  name = forms.CharField(label="User name:",
               required=True,
               widget=forms.TextInput(attrs={'size': 50,}),
               help_text="",
               error_messages={'required': 
               '''Please enter the QGIS user's name'''},
              )
  email = forms.EmailField(label="Email:",
               required=True,
               widget=forms.TextInput(attrs={'size': 50,}),
               help_text="This will not be displayed on the map",
               error_messages={'required': 
               '''Please enter the email address you wish to use'''},
              )
  home_url = forms.URLField(label="User home page:",
               required=False,
               widget=forms.TextInput(attrs={'size': 50,}),
               help_text="",
             )    
  image = forms.ImageField(label="User profile picture:",
               required=False,
               help_text="",
             )
  geometry = forms.CharField(label="User location:",
               required=True,
               widget=EditableMap(),
               help_text="Please enter your base location",
               error_messages={'required': 
               '''A location is required'''},
              )                           
            
  class Meta:
    model = QgisUser
    exclude = ('added_date', 'guid',)
    
class LoginForm(ModelForm):
  guid = forms.CharField(label="User id:",
               required=True,
               widget=forms.TextInput(attrs={'size': 50,}),
               help_text="",
               error_messages={'required': 
               '''Please enter your user id'''},
              )
  class Meta:
    model = QgisUser
    exclude = ('added_date', 'email', 'home_url', 'image', 'geometry',)    
    
   



