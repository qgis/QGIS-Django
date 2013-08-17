# -*- coding: utf-8 -*-

from django import forms
from taggit.forms import *

class StyleUploadForm(forms.Form):
    """The form to upload a style qml file exported by QGIS"""
    xmlfile = forms.FileField()
    tags = TagField()
    name = forms.CharField(max_length=256)
    desc = forms.CharField()
