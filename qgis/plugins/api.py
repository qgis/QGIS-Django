from plugins.models import *

from tastypie.resources import ModelResource



class PluginResource(ModelResource):
    class Meta:
        queryset = Plugin.objects.all()
        resource_name = 'plugin'


class PluginVersionResource(ModelResource):
    class Meta:
        queryset = PluginVersion.objects.all()
        resource_name = 'version'

