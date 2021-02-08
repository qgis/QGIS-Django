from django.urls import include, path

from api.views import ResourceAPIList, ResourceAPIDownload



urlpatterns = [
    # path('rest-auth/', include('rest_auth.urls')),
    # # API
    # path('geopackages/', geopackage.GeopackageAPIList.as_view(),
    #      name='geopackage-list'),
    # path('geopackages/<int:pk>/', geopackage.GeopackageAPIDetail.as_view(),
    #      name='geopackage-detail'),
    # path('geopackages/<int:pk>/download/', geopackage.GeopackageAPIDownload.as_view(),
    #      name='geopackage-download'),
    path('', ResourceAPIList.as_view(), name='resource-list'),
    path('<resource_type>/<int:id>/', ResourceAPIDownload.as_view(),
         name='resource-download')

]