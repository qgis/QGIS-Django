# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.utils.translation import ugettext_lazy as _

# Plugins
urlpatterns = patterns('django.views.generic.list_detail',
    url(r'^$', 'object_list', { 'queryset' : Plugin.published_objects.all()}, name = 'published_plugins'),
    url(r'^(?P<object_id>[0-9]+)/$', 'object_detail', { 'queryset' : Plugin.objects.all() }, name = 'plugin_detail'),
    url(r'^community-map/$', 'object_list', {'queryset' : Plugin.featured_objects.all(), 'extra_context' : {'title' : _('Featured plugins')}}, name = 'featured_plugins'),
    url(r'^unpublished/$', 'object_list', {'queryset' : Plugin.unpublished_objects.all(), 'extra_context' : {'title' : _('Unpublished plugins')}}, name = 'unpublished_plugins'),
    url(r'^fresh/$', 'object_list', {'queryset' : Plugin.fresh_objects.all(), 'extra_context' : {'title' : _('Fresh plugins')}}, name = 'fresh_plugins'),
    url(r'^stable/$', 'object_list', {'queryset' : Plugin.stable_objects.all(), 'extra_context' : {'title' : _('Stable plugins')}}, name = 'stable_plugins'),
    url(r'^experimental/$', 'object_list', {'queryset' : Plugin.experimental_objects.all(), 'extra_context' : {'title' : _('Experimental plugins')}}, name = 'experimental_plugins'),
    url(r'^popular/$', 'object_list', {'queryset' : Plugin.popular_objects.all(), 'extra_context' : {'title' : _('Popular plugins')}}, name = 'popular_plugins'),
    # XML
    url(r'^plugins.xml$', 'object_list', {'queryset' : Plugin.published_objects.all(), 'template_name' : 'plugins/plugins.xml', 'mimetype' : 'text/xml' }, name = 'xml_plugins'),
 )

view_users  %}">{% trans "Community map"%}</a></li>
                <li><a href="{% url create_user_form %}">{% trans "Add new user"%}</a></li>
                <li><a href="{% url delete_user %}">{
