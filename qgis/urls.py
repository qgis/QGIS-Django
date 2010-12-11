from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib.auth.views import login, logout

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
    # TIM: snippets app
    (r'^snippets/', include('cab.urls.snippets')),
    (r'^tags/', include('cab.urls.tags')),
    (r'^bookmarks/', include('cab.urls.bookmarks')),
    (r'^languages/', include('cab.urls.languages')),
    (r'^popular/', include('cab.urls.popular')),
)

#ABP: temporary home page
urlpatterns += patterns('django.views.generic.simple',
    url(r'^$', 'direct_to_template', {'template': 'index.html'}, name = 'index'),
)


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
