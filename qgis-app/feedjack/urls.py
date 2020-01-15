# -*- coding: utf-8 -*-

"""
feedjack
Gustavo Picón
urls.py
"""

from django.views.generic.base import RedirectView
from django.conf.urls import url

from feedjack import views



urlpatterns = [
    url(r'^rss20.xml$', RedirectView.as_view(url='/feed/rss/')),
    url(r'^feed/$', RedirectView,
      {'url':'/feed/atom/'}),
    url(r'^feed/rss/$', views.rssfeed),
    url(r'^feed/atom/$', views.atomfeed),

    url(r'^feed/user/(?P<user>\d+)/tag/(?P<tag>.*)/$', RedirectView.as_view(url='/feed/atom/user/%(user)s/tag/%(tag)s/')),
    url(r'^feed/user/(?P<user>\d+)/$', RedirectView.as_view(url='/feed/atom/user/%(user)s/')),
    url(r'^feed/tag/(?P<tag>.*)/$', RedirectView.as_view(url='/feed/atom/tag/%(tag)s/')),

    url(r'^feed/atom/user/(?P<user>\d+)/tag/(?P<tag>.*)/$', views.atomfeed),
    url(r'^feed/atom/user/(?P<user>\d+)/$', views.atomfeed),
    url(r'^feed/atom/tag/(?P<tag>.*)/$', views.atomfeed),
    url(r'^feed/rss/user/(?P<user>\d+)/tag/(?P<tag>.*)/$', views.rssfeed),
    url(r'^feed/rss/user/(?P<user>\d+)/$', views.rssfeed),
    url(r'^feed/rss/tag/(?P<tag>.*)/$', views.rssfeed),

    url(r'^user/(?P<user>\d+)/tag/(?P<tag>.*)/$', views.mainview),
    url(r'^user/(?P<user>\d+)/$', views.mainview),
    url(r'^tag/(?P<tag>.*)/$', views.mainview),

    url(r'^opml/$', views.opml),
    url(r'^foaf/$', views.foaf),
    url(r'^$', views.mainview),
]
