# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('symbols.views',
        url(r'^$','index'),

        # XML Responses for desktop
        url(r'^tags.xml$','tags'),
        url(r'^tag/(?P<tag_id>\d+)/$', 'symbols_with_tagid'),
        url(r'^tag/(?P<tag>\w+)/$', 'symbols_with_tag'),
        url(r'^authors.xml$', 'authors'),
        url(r'^author/(?P<authid>\d+)/$', 'symbols_by_author'),
        url(r'^name/(?P<symname>\w+)/$','symbol_with_name'),
        url(r'^type/(?P<typename>\w+)/$', 'symbols_of_type'),
        url(r'^search/$', 'search'),

        # Form to upload symbols
        url(r'^add/','add_symbol', name='symbol_upload_link'),
        url(r'^up_thanks/', 'upload_thanks')

        )
