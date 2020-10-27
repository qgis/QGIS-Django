from django.conf.urls import url

from .views import StyleListView, StyleDetailView, style_download

urlpatterns = [
    url(r'^$', StyleListView.as_view(), name='style_list'),
    url(r'^(?P<name>[A-Za-z0-9-_ ]+)/$', StyleDetailView.as_view(), name='style_detail'),
    url(r'^(?P<name>[A-Za-z0-9-_ ]+)/download$', style_download, name='style_download'),

]
