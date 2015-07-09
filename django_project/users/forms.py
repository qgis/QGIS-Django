from users.models import *
from django import forms
from django.conf import settings
from django.forms import ModelForm, Textarea, TextInput

from olwidget.widgets import EditableMap
from olwidget.forms import MapModelForm
from olwidget.fields import MapField, EditableLayerField, InfoLayerField
from olwidget import utils



from users.models import QgisUser

class QgisUserForm(MapModelForm):
  name = forms.CharField(label="Your name:",
               required=True,
               widget=forms.TextInput(attrs={'size': 50,}),
               help_text="",
               error_messages={'required':
               'Please enter the QGIS user\'s name'},
              )
  email = forms.EmailField(label="Email:",
               required=True,
               widget=forms.TextInput(attrs={'size': 50,}),
               help_text="This will not be displayed on the map",
               error_messages={'required':
               'Please enter the email address you wish to use'},
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
               widget=EditableMap(
                 options = { 'layers': ['osm.mapnik'] }
               ),
               help_text="To add your location: click 'Edit' on the top-right corner of the map, and then the pencil icon",
               error_messages={'required':
               'A location is required'},
              )

  def clean_geometry(self):
      data = self.cleaned_data['geometry']
      try:
        utils.get_ewkt(data)
      except:
        self.cleaned_data['geometry'] = ''
        self.data['geometry']= ''
        raise forms.ValidationError("Invalid geometry")
      # Always return the cleaned data, whether you have changed it or
      # not.
      return data

  class Meta:
    model = QgisUser
    exclude = ('added_date', 'guid',)

class EmailForm(forms.Form):
  email = forms.EmailField(label="Email:",
               required=True,
               help_text="",
               error_messages={'required':
               'A valid email is required'},)




