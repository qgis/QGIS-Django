from django.urls import path

from api.views import ResourceAPIList, ResourceAPIDownload


urlpatterns = [
    path('resources/', ResourceAPIList.as_view(), name='resource-list'),
    path('resource/<uuid:uuid>/', ResourceAPIDownload.as_view(),
         name='resource-download')
]
