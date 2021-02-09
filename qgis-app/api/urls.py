from django.urls import path

from api.views import ResourceAPIList, ResourceAPIDownload


urlpatterns = [

    path('', ResourceAPIList.as_view(), name='resource-list'),
    path('<resource_type>/<int:id>/', ResourceAPIDownload.as_view(),
         name='resource-download')
]
