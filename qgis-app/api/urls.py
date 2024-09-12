from api.views import ResourceAPIDownload, ResourceAPIList
from django.urls import path
from django.urls import re_path as url
from api.views import HubTokenDetailView, HubTokenListView, hub_token_create
urlpatterns = [
    path("resources/", ResourceAPIList.as_view(), name="resource-list"),
    path(
        "resource/<uuid:uuid>/", ResourceAPIDownload.as_view(), name="resource-download"
    ),
    url(
        r"^tokens/$",
        HubTokenListView.as_view(),
        name="hub_token_list",
    ),
    url(
        r"^tokens/(?P<pk>\d+)/$",
        HubTokenDetailView.as_view(),
        name="hub_token_detail",
    ),
    url(
        r"^tokens/create/$",
        hub_token_create,
        {},
        name="hub_token_create",
    ),

]
