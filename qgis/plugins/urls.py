# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from plugins.models import Plugin, PluginVersion

# Plugins
urlpatterns = patterns('django.views.generic.list_detail',
    url(r'^$', 'object_list', { 'queryset' : Plugin.published_objects.all() }, name = 'published_plugins'),
    url(r'^(?P<object_id>[0-9]+)/$', 'object_detail', { 'queryset' : Plugin.objects.all() }, name = 'plugin_detail'),
    url(r'^featured/$', 'object_list', {'queryset' : Plugin.featured_objects.all()}, name = 'featured_plugins'),
    url(r'^unpublished/$', 'object_list', {'queryset' : Plugin.unpublished_objects.all()}, name = 'unpublished_plugins'),
    url(r'^fresh/$', 'object_list', {'queryset' : Plugin.fresh_objects.all()}, name = 'fresh_plugins'),
    url(r'^stable/$', 'object_list', {'queryset' : Plugin.stable_objects.all()}, name = 'stable_plugins'),
    url(r'^experimental/$', 'object_list', {'queryset' : Plugin.experimental_objects.all()}, name = 'experimental_plugins'),
)

# Plugins filtered views (need user parameter from request)
urlpatterns += patterns('plugins.views',
    url(r'^my/$', 'my_plugins', {}, name = 'my_plugins'),
)

# Management
urlpatterns += patterns('plugins.views',
    url(r'^add/$', 'plugin_upload', {}, name = 'plugin_upload'),
    url(r'^delete/(?P<plugin_id>[0-9]+)/$', 'plugin_delete', {}, name = 'plugin_delete'),
    url(r'^update/(?P<plugin_id>[0-9]+)/$', 'plugin_update', {}, name = 'plugin_update'),
    url(r'^version/(?P<plugin_id>[0-9]+)/add/$', 'version_create', {}, name = 'version_create'),
    url(r'^version/(?P<version_id>[0-9]+)/delete/$', 'version_delete', {}, name = 'version_delete'),
    url(r'^version/(?P<version_id>[0-9]+)/update/$', 'version_update', {}, name = 'version_update'),
    url(r'^version/(?P<version_id>[0-9]+)/download/$', 'version_download', {}, name = 'version_download'),
)

