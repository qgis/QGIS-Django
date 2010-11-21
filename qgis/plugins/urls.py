# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.views.generic.list_detail import object_list
from plugins.models import Plugin, PluginVersion

info_dict =  {
    'query_set' : Plugin.objects.all(),
    'paginate_by' : 10,
}

urlpatterns = patterns('',
    (r'^$', object_list, info_dict),
)
