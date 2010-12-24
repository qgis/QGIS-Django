from django.contrib.gis import admin
from models import *

class QgisUsersAdmin(admin.GeoModelAdmin):
  field = (None, {'fields': ('name')})
  field = (None, {'fields': ('email')})
  field = (None, {'fields': ('wkb_geometry')})
  list_display = ('name', 'email', 'wkb_geometry') 


#Register each model with its associated admin class
admin.site.register(QgisUser, QgisUsersAdmin)

