# -*- coding: utf-8 -*-
from symbols.models import Symbol
from symbols.forms import SymbolUploadForm
from symbols.utils import SymbolExtractor

from taggit.models import TaggedItem, Tag

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.template import RequestContext

from xml.dom.minidom import getDOMImplementation

def index(request):
    return render_to_response("/symbols/s_index.html", {}, context_instance=RequestContext(request) )

def tags(request):
    queryset = TaggedItem.objects.filter(content_type__app_label="symbols")
    tag_ids = queryset.values_list('tag_id', flat=True)
    tags = Tag.objects.filter(id__in=tag_ids)
    # create a xml with the list of the tag.name for tag in tags
    domimp = getDOMImplementation()
    doc = domimp.createDocument(None, "symbol_tags", None)
    root_ele = doc.documentElement
    for tag in tags:
        tag_ele = doc.createElement("tag")
        tagnode = doc.createTextNode(tag.name)
        tag_ele.appendChild(tagnode)
        root_ele.appendChild(tag_ele)
    return HttpResponse(root_ele.toxml(), content_type="application/xhtml+xml")

def symbols_with_tag(request, tag_id):
    op = "Request recieved for symbol with tag id" + str(tag_id)
    return HttpResponse(op)

@login_required
def add_symbol(request):
    op = "symbols uploader is under construc..."
    if request.method == 'POST':
        form = SymbolUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Handle the file with the cleaned data.. save the symbols to the DB
            xmlfile = request.FILES['xmlfile']
            tags = form.cleaned_data['tags']
            extract = SymbolExtractor(xmlfile)
            for sym in extract.symbols():
                # Create the symbol object to save in the database
                obj = Symbol()
                obj.created_by = request.user
                obj.name = sym["name"]
                obj.xml = sym["xml"]
                obj.save()
                # add the tags via taggit after saving the symbol
                for tag in tags:
                    obj.tags.add(tag)
            return HttpResponseRedirect('/symbols/up_thanks/')
    else:
        form = SymbolUploadForm()
    return render_to_response('/symbols/s_upload.html', {'form' : form, }, context_instance=RequestContext(request))

def upload_thanks(request):
    op = "Your symbols has been added to the repository"
    return HttpResponse(op)


