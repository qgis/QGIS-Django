# -*- coding: utf-8 -*-
from symbols.models import Symbol, ColorRamp, Group, Tag
from django.http import HttpResponse

def index(request):
    op = "Welcome to the new Symbols Page"
    return HttpResponse(op)

def tags(request):
    op = "You are now requesting all the tags"
    return HttpResponse(op)

def groups(request):
    op = "You are requesting the groups hierarchy"
    return HttpResponse(op)

def symbols_with_tag(request, tag_id):
    op = "Request recieved for symbol with tag id" + str(tag_id)
    return HttpResponse(op)

def symbols_of_group(request, group_id):
    op = "Request recieved for symbols under the group id " + str(group_id)
    return HttpResponse(op)

def add_symbol(request):
    op = "symbols uploader is under construc..."
    return HttpResponse(op)

def add_colorramp(request):
    op = "colorramp uploader is under construc..."
    return HttpResponse(op)

