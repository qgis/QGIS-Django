# -*- coding: utf-8 -*-
from django.db import models

# import auth users for owners
from django.contrib.auth.models import User

from taggit.managers import TaggableManager

class Style (models.Model):
    name = models.CharField(max_length="256")
    xml = models.TextField()
    description = models.TextField()
    tags = TaggableManager()
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    created_by = models.ForeignKey(User, verbose_name='Created by', related_name="styles")
    # Properties
    qgis_version = models.CharField(max_length="128")
    min_scale = models.FloatField()
    max_scale = models.FloatField()
    min_label_scale = models.FloatField()
    max_label_scale = models.FloatField()
    scale_flag = models.BooleanField() # scale based visibility flag
    label_scale_flag = models.BooleanField() # scale based Label visibility flag
    renderer_type = models.CharField(max_length="256")


    def __unicode__(self):
        return self.name

