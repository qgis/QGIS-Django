from django.conf.urls import include, url
from django.conf import settings
from django.views.generic.base import RedirectView
from django.views.static import serve
from django.contrib.auth.views import login, logout
# to find users app views
from users.views import *
from homepage import homepage
# Menu system, registration of views is at the end of this file
import simplemenu
from django.contrib.flatpages.models import FlatPage

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns =[
    # Example:
    # (r'^qgis/', include('qgis.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # ABP: plugins app
    url(r'^plugins/', include('plugins.urls')),
    #(r'^tags/', include('cab.urls.tags')),
    #(r'^bookmarks/', include('cab.urls.bookmarks')),
    #(r'^languages/', include('cab.urls.languages')),
    #(r'^popular/', include('cab.urls.popular')),
    url(r'^search/', include('haystack.urls')),
    url(r'^search/', include('custom_haystack_urls')),

    # SAM: qgis-users app
    url(r'^community-map/', include('users.urls')),
    # Fix broken URLS in feedjack
    url(r'^planet/feed/$', RedirectView.as_view(url='/planet/feed/atom/')),
    # Tim: Feedjack feed aggregator / planet
    url(r'^planet/', include('feedjack.urls')),
    # ABP: autosuggest for tags
    url(r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),
    url(r'^userexport/', include('userexport.urls')),

]

# ABP: temporary home page
#urlpatterns += patterns('django.views.generic.simple',
#    url(r'^$', 'direct_to_template', {'template': 'index.html'}, name = 'index'),
#)


# serving static media
if settings.SERVE_STATIC_MEDIA:
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]


# auth
urlpatterns += [
    url(r'^accounts/login/$',  login, {}, name = 'fe_login'),
    url(r'^accounts/logout/$', logout, {}, name = 'fe_logout'),
]

# tinymce
urlpatterns += [
    url(r'^tinymce/', include('tinymce.urls')),
]


# Home
urlpatterns += [
    url(r'^$', homepage),
]

simplemenu.register(
    '/admin/',
    '/planet/',
    '/community-map/',
    '/plugins/',
    FlatPage.objects.all(),
    simplemenu.models.URLItem.objects.all(),
)
