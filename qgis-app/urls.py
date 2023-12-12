import simplemenu
from django.conf import settings
from django.conf.urls import url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.urls import include, path
from django.views.generic.base import RedirectView
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

# to find users app views
# from users.views import *
from homepage import homepage
from rest_framework import permissions

admin.autodiscover()


schema_view = get_schema_view(
    openapi.Info(
        title="Hub API",
        default_version="v1",
        description="Hub API for sharing files application",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="email@example.com"),
        license=openapi.License(name="CC"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Example:
    # (r'^qgis/', include('qgis.foo.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    # Uncomment the next line to enable the admin:
    url(r"^admin/", admin.site.urls),
    # ABP: plugins app
    url(r"^plugins/", include("plugins.urls")),
    # (r'^tags/', include('cab.urls.tags')),
    # (r'^bookmarks/', include('cab.urls.bookmarks')),
    # (r'^languages/', include('cab.urls.languages')),
    # (r'^popular/', include('cab.urls.popular')),
    url(r"^search/", include("custom_haystack_urls")),
    url(r"^search/", include("haystack.urls")),
    # AG: User Map
    # url(r'^community-map/', include('user_map.urls', namespace='user_map')),
    # Fix broken URLS in feedjack
    # url(r'^planet/feed/$', RedirectView.as_view(url='/planet/feed/atom/')),
    # Tim: Feedjack feed aggregator / planet
    url(r"^planet/", include("feedjack.urls")),
    # ABP: autosuggest for tags
    url(r"^taggit_autosuggest/", include("taggit_autosuggest.urls")),
    url(r"^userexport/", include("userexport.urls")),
    # Styles and other files sharing
    url(r"^styles/", include("styles.urls")),
    url(r"^geopackages/", include("geopackages.urls")),
    url(r"^layerdefinitions/", include("layerdefinitions.urls")),
    url(r"^models/", include("models.urls")),
    url(r"^wavefronts/", include("wavefronts.urls")),
]

# ABP: temporary home page
# urlpatterns += patterns('django.views.generic.simple',
#    url(r'^$', 'direct_to_template', {'template': 'index.html'}, name = 'index'),
# )


# serving static media
from django.conf.urls.static import static

if settings.SERVE_STATIC_MEDIA:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# auth
urlpatterns += [
    path("accounts/", include("django.contrib.auth.urls")),
]

# tinymce
urlpatterns += [
    url(r"^tinymce/", include("tinymce.urls")),
]


# Home
urlpatterns += [
    url(r"^$", homepage),
]

# API
urlpatterns += [
    url(r"^api/v1/", include("api.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r"^__debug__/", include(debug_toolbar.urls)),
    ]

simplemenu.register(
    "/admin/",
    "/planet/",
    #    '/community-map/',
    "/plugins/",
    "/styles/?order_by=-upload_date&&is_gallery=true",
    "/geopackages/?order_by=-upload_date&&is_gallery=true",
    "/layerdefinitions/?order_by=-upload_date&&is_gallery=true",
    "/models/?order_by=-upload_date&&is_gallery=true",
    "/wavefronts/?order_by=-upload_date&&is_gallery=true",
    FlatPage.objects.all(),
    simplemenu.models.URLItem.objects.all(),
)
