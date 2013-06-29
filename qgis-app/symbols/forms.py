# -*- coding: utf-8 -*-

from django import forms
from taggit.forms import *

class SymbolUploadForm(forms.Form):
    """The form to upload a set of symbols exported by QGIS"""
    xmlfile = forms.FileField()
    tags = TagField()
