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

from xml.dom.minidom import getDOMImplementation, parseString

def index(request):
    op = "Be hell with the home page"
    return render_to_response("/symbols/s_index.html", {}, context_instance=RequestContext(request) )

def tags(request):
    queryset = TaggedItem.objects.filter(content_type__app_label="symbols")
    tag_ids = queryset.values_list('tag_id', flat=True)
    tags = Tag.objects.filter(id__in=tag_ids)
    # create a xml with the list of the tag.name for tag in tags
    domimp = getDOMImplementation()
    doc = domimp.createDocument(None, "tags", None)
    root_ele = doc.documentElement
    for tag in tags:
        tag_ele = doc.createElement("tag")
        tagnode = doc.createTextNode(tag.name)
        tag_ele.appendChild(tagnode)
        root_ele.appendChild(tag_ele)
    return HttpResponse(root_ele.toxml(), content_type="application/xhtml+xml")

def symbols_with_tag(request, tag):
    doc = getDOMImplementation().createDocument(None, "qgis_style", None)
    style_ele = doc.documentElement
    style_ele.setAttribute("version", "1")
    symbols_ele = doc.createElement("symbols")
    style_ele.appendChild(symbols_ele)
    symbols = Symbol.objects.filter(tags__name__in=[tag])
    for symbol in symbols:
        symdom = parseString(symbol.xml).documentElement
        symbols_ele.appendChild(symdom)
    return HttpResponse(style_ele.toxml(), content_type="application/xhtml+xml")

def authors(request):
    users = User.objects.all()
    # create a xml with the list of the authors
    domimp = getDOMImplementation()
    doc = domimp.createDocument(None, "authors", None)
    root_ele = doc.documentElement
    for user in users:
        symbols = user.symbols.all()
        if len(symbols) > 0:
            auth_ele = doc.createElement("author")
            authnode = doc.createTextNode(unicode(user))
            auth_ele.appendChild(authnode)
            auth_ele.setAttribute("id", unicode(user.pk))
            root_ele.appendChild(auth_ele)
    return HttpResponse(root_ele.toxml(), content_type="application/xhtml+xml")

def symbols_by_author(request, authid):
    doc = getDOMImplementation().createDocument(None, "qgis_style", None)
    style_ele = doc.documentElement
    style_ele.setAttribute("version", "1")
    symbols_ele = doc.createElement("symbols")
    style_ele.appendChild(symbols_ele)
    symbols = Symbol.objects.filter(created_by=authid)
    for symbol in symbols:
        symdom = parseString(symbol.xml).documentElement
        symbols_ele.appendChild(symdom)
    return HttpResponse(style_ele.toxml(), content_type="application/xhtml+xml")

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
                obj.stype = sym["type"]
                obj.save()
                # add the tags via taggit after saving the symbol
                for tag in tags:
                    obj.tags.add(tag)
            return HttpResponseRedirect('/symbols/up_thanks/')
    else:
        form = SymbolUploadForm()
    return render_to_response('/symbols/s_upload.html', {'form' : form, }, context_instance=RequestContext(request))

def upload_thanks(request):
    op = "Your symbols has been added to the repository. <a href=\"/symbols/\">Click Here</a> to go back."
    return HttpResponse(op)


