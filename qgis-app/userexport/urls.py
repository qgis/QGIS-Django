# -* coding:utf-8 *- #
from django.conf.urls import *
# Custom

urlpatterns = patterns('',

    url(r'^export', 'userexport.views.export', {}, name = 'userexport'),

)
