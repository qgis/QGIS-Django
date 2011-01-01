# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

# our base class
from django.db import models
# import GeoDjango stuff to support spatial data types
from django.contrib.gis.db import models
# use python time goodies
import datetime
import uuid

class QgisUser(models.Model):
    wkb_geometry = models.PointField(srid=4326,null=True, blank=True)
    name = models.TextField() 
    email = models.TextField() 
    image = models.TextField() # This field type is a guess.
    home_url = models.TextField() # This field type is a guess.
    added_date = models.DateTimeField('DateAdded', 
                auto_now=True, auto_now_add=False)
    guid = models.CharField(max_length=40)
    objects = models.GeoManager()
    
    def save(self):
      #makes a random globally unique id
      if not self.guid or self.guid=='null':
      self.guid = str(uuid.uuid4())
      super(QgisUser, self).save() 

    class Meta:
        db_table = u'qgis_users'
        verbose_name = ('QGIS User')
        verbose_name_plural = ('QGIS Users')
        ordering = ('name',)
        
       
                

