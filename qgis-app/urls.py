from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib.auth.views import login, logout
# to find users app views
from users.views import *

# Menu system, registration of views is at the end of this file
import simplemenu
from django.contrib.flatpages.models import FlatPage

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Example:
    # (r'^qgis/', include('qgis.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # ABP: plugins app
    (r'^plugins/', include('plugins.urls')),
    #(r'^tags/', include('cab.urls.tags')),
    #(r'^bookmarks/', include('cab.urls.bookmarks')),
    #(r'^languages/', include('cab.urls.languages')),
    #(r'^popular/', include('cab.urls.popular')),
    (r'^search/', include('haystack.urls')),
    (r'^search/', include('custom_haystack_urls')),

    # SAM: qgis-users app
    (r'^community-map/', include('users.urls')),
    # Tim: Feedjack feed aggregator / planet
    (r'^planet/', include('feedjack.urls')),
    # ABP: autosuggest for tags
    (r'^taggit_autosuggest/', include('taggit_autosuggest.urls')),

)

# ABP: temporary home page
#urlpatterns += patterns('django.views.generic.simple',
#    url(r'^$', 'direct_to_template', {'template': 'index.html'}, name = 'index'),
#)


# serving static media
if settings.SERVE_STATIC_MEDIA:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )


# auth
urlpatterns += patterns('',
    url(r'^accounts/login/$',  login, {}, name = 'fe_login'),
    url(r'^accounts/logout/$', logout, {}, name = 'fe_logout'),
)

# tinymce
urlpatterns += patterns('',
    (r'^tinymce/', include('tinymce.urls')),
)


# Home
urlpatterns += patterns('homepage',
    (r'^$', 'homepage'),
)

simplemenu.register(
    '/admin/',
    '/planet/',
    '/community-map/',
    '/plugins/',
    FlatPage.objects.all(),
    simplemenu.models.URLItem.objects.all(),
)
