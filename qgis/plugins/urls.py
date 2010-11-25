# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from plugins.models import Plugin, PluginVersion

info_dict =  {
    'queryset' : Plugin.objects.filter(published = True),
}

detail_info_dict = {
    'queryset' : Plugin.objects.all(),
}

# Plugins
urlpatterns = patterns('django.views.generic.list_detail',
    url(r'^$', 'object_list', info_dict, name = 'plugins_list'),
    url(r'^(?P<object_id>[0-9]+)/$', 'object_detail', detail_info_dict, name = 'plugin_detail'),
)

# Management
urlpatterns += patterns('plugins.views',
    url(r'^add/$', 'plugin_create', {}, name = 'plugin_create'),
    url(r'^delete/(?P<plugin_id>[0-9]+)/$', 'plugin_delete', {}, name = 'plugin_delete'),
    url(r'^update/(?P<plugin_id>[0-9]+)/$', 'plugin_update', {}, name = 'plugin_update'),
    url(r'^version/(?P<plugin_id>[0-9]+)/add/$', 'version_create', {}, name = 'version_create'),
    url(r'^version/(?P<version_id>[0-9]+)/delete/$', 'version_delete', {}, name = 'version_delete'),
    url(r'^version/(?P<version_id>[0-9]+)/update/$', 'version_update', {}, name = 'version_update'),
    url(r'^version/(?P<version_id>[0-9]+)/download/$', 'version_download', {}, name = 'version_download'),

)

