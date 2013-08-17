# -*- coding: utf-8 -*-
from styles.models import Style
from styles.forms import StyleUploadForm
from styles.utils import StyleDataExtractor

from taggit.models import TaggedItem, Tag

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.template import RequestContext


def index(request):
    return render_to_response("/styles/st_index.html", {}, context_instance=RequestContext(request) )

@login_required
def add_style(request):
    if request.method == 'POST':
        form = StyleUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle the file with the cleaned data.. save the style as such
            xmlfile = request.FILES['xmlfile']
            tags = form.cleaned_data['tags']
            name = form.cleaned_data['name']
            desc = form.cleaned_data['desc']
            # Extract the style specific data
            dataExt = StyleDataExtractor(xmlfile)
            obj = Style()
            obj.created_by = request.user
            obj.name = form.cleaned_data['name']
            obj.xml = dataExt.styleAsString()
            obj.description = form.cleaned_data['desc']

            # Properties
            data = dataExt.styledata()
            obj.qgis_version = data["version"]
            obj.min_scale =  float(data["minScale"])
            obj.max_scale = float(data["maxScale"])
            obj.min_label_scale = float(data["minLblScale"])
            obj.max_label_scale = float(data["minLblScale"])
            obj.scale_flag = data["scaleFlag"]
            obj.label_scale_flag = data["lblScaleFlag"]
            obj.renderer_type = data["renderer"]
            obj.save()

            for tag in tags:
                obj.tags.add(tag)

            return HttpResponseRedirect('/styles/up_thanks/')

    else:
        form = StyleUploadForm()
    return render_to_response('/styles/st_upload.html', {'form' : form, }, context_instance=RequestContext(request))

def upload_thanks(request):
    op = "Your style has been added to the repository. <a href=\"/styles/\">Click Here</a> to go back."
    return HttpResponse(op)


