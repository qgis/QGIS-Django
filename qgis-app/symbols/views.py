# -*- coding: utf-8 -*-
from symbols.models import Symbol
from symbols.forms import SymbolUploadForm
from symbols.utils import SymbolExtractor

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.template import RequestContext


def index(request):
    op = "Welcome to the new Symbols Page"
    return HttpResponse(op)

def tags(request):
    op = "You are now requesting all the tags"
    return HttpResponse(op)

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


