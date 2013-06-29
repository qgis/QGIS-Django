# -*- coding: utf-8 -*-
from django.db import models
# import auth users for owners
from django.contrib.auth.models import User

from taggit.managers import TaggableManager

# TODO add the image bitmap field to the models

class Symbol (models.Model):
    name = models.CharField(max_length="256")
    xml = models.TextField()
    tags = TaggableManager()
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(User, verbose_name='Created by')
    # Indicate Symbol or colorramp
    is_symbol = models.BooleanField(default=True, db_index=True)

    def __unicode__(self):
        return self.name

