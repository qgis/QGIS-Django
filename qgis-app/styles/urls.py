# -*- coding: utf-8 -*-
from django.conf.urls import *
from django.views.generic import ListView, DetailView
from styles.models import Style

# place app url patterns here
urlpatterns = patterns('styles.views',
        url(r'^$','index'),

        url(r'^list/$', ListView.as_view( model=Style ) ),
        url(r'^list.xml$', 'xml_list' ),
        url(r'^tags.xml$', 'tags'),

        url(r'tag/(?P<tag_id>\d+)/$', 'styles_with_tagid'),
        url(r'tag/(?P<tag>\w+)/$', 'styles_with_tag'),

        url(r'^(?P<pk>\d+)/detail/$', DetailView.as_view( model=Style )),
        url(r'^(?P<pk>\d+)/$', 'download' ),

        # Form to upload styles
        url(r'^add/','add_style', name='style_upload_link'),
        url(r'^up_thanks/', 'upload_thanks')

        )
