from django.conf.urls import url

from .views import home_page_view

urlpatterns = [
    url(r'^$', home_page_view, name='home')
]
