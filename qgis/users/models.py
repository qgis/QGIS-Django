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

class QgisUser(models.Model):
    ogc_fid = models.IntegerField(primary_key=True)
    wkb_geometry = models.PointField(srid=4326,null=True, blank=True)
    id = models.DecimalField(max_digits=10, decimal_places=0)
    name = models.TextField() # This field type is a guess.
    email = models.TextField() # This field type is a guess.
    image = models.TextField() # This field type is a guess.
    image_url = models.TextField() # This field type is a guess.
    home_url = models.TextField() # This field type is a guess.
    country_id = models.TextField() # This field type is a guess.
    place_desc = models.TextField() # This field type is a guess.
    admin_note = models.TextField() # This field type is a guess.
    lat = models.DecimalField(max_digits=24, decimal_places=15)
    long = models.DecimalField(max_digits=24, decimal_places=15)
    added_date = models.TextField() # This field type is a guess.
    checked_da = models.TextField() # This field type is a guess.
    verified = models.TextField() # This field type is a guess.
    hash = models.TextField() # This field type is a guess.
    objects = models.GeoManager()

    class Meta:
        db_table = u'qgis_users'
        verbose_name = ('QGIS User')
        verbose_name_plural = ('QGIS Users')
        ordering = ('name',)



