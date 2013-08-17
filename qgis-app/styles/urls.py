# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

# place app url patterns here
urlpatterns = patterns('styles.views',
        url(r'^$','index'),

        # Form to upload styles
        url(r'^add/','add_style', name='style_upload_link'),
        url(r'^up_thanks/', 'upload_thanks')

        )
