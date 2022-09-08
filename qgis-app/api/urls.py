from api.views import ResourceAPIDownload, ResourceAPIList
from django.urls import path

urlpatterns = [
    path("resources/", ResourceAPIList.as_view(), name="resource-list"),
    path(
        "resource/<uuid:uuid>/", ResourceAPIDownload.as_view(), name="resource-download"
    ),
]
