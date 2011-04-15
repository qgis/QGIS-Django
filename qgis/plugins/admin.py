from plugins.models import Plugin, PluginVersion
from django.contrib.gis import admin


class PluginAdmin (admin.ModelAdmin):
    list_filter     = ('featured',)
    list_display    = ('name', 'featured', 'created_by', 'created_on', 'downloads', 'stable', 'experimental')


class PluginVersionAdmin (admin.ModelAdmin):
    list_filter     = ('experimental', 'approved', 'plugin')
    list_display    = ('plugin', 'approved', 'version', 'experimental', 'created_on', 'downloads')



admin.site.register(Plugin, PluginAdmin)
admin.site.register(PluginVersion, PluginVersionAdmin)
