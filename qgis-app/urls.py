from django.urls import include, path
from django.conf import settings
from django.conf.urls import url
from django.views.generic.base import RedirectView
from django.views.static import serve
# to find users app views
#from users.views import *
from homepage import homepage
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
    url(r'^admin/', admin.site.urls),

    # ABP: plugins app
    url(r'^plugins/', include('plugins.urls')),
    #(r'^tags/', include('cab.urls.tags')),
    #(r'^bookmarks/', include('cab.urls.bookmarks')),
    #(r'^languages/', include('cab.urls.languages')),
    #(r'^popular/', include('cab.urls.popular')),
    #url(r'^search/', include('custom_haystack_urls')),
    #url(r'^search/', include('haystack.urls')),

    # AG: User Map
    #url(r'^community-map/', include('user_map.urls', namespace='user_map')),
    # Fix broken URLS in feedjack
    #url(r'^planet/feed/$', RedirectView.as_view(url='/planet/feed/atom/')),
    # Tim: Feedjack feed aggregator / planet
    #url(r'^planet/', include('feedjack.urls')),
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
    path('accounts/', include('django.contrib.auth.urls')),
]

# tinymce
urlpatterns += [
    url(r'^tinymce/', include('tinymce.urls')),
]


# Home
urlpatterns += [
    url(r'^$', homepage),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
