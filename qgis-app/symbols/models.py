# -*- coding: utf-8 -*-
from django.db import models
# import auth users for owners
from django.contrib.auth.models import User
# For permalinks
from django.core.urlresolvers import reverse
from django.conf import settings
import datetime, os, re
from djangoratings.fields import AnonymousRatingField

# TODO add the image bitmap field to the models
# TODO add Author details

class Group (models.Model):
    name = models.CharField(max_length="256")
    parent = models.ForeignKey('self')

    def __unicode__(self):
        return self.name

class Tag (models.Model):
    name = models.CharField(max_length="256")

    def __unicode__(self):
        return self.name

class Symbol (models.Model):
    name = models.CharField(max_length="256")
    xml = models.TextField()
    group = models.ForeignKey(Group)
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        return self.name

class ColorRamp (models.Model):
    name = models.CharField(max_length="256")
    xml = models.TextField()
    group = models.ForeignKey(Group)
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        return self.name
