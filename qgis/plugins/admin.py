from plugins.models import Plugin, PluginVersion
from django.contrib.gis import admin


class PluginAdmin (admin.ModelAdmin):
    list_filter     = ('published', 'featured')
    list_display    = ('name', 'published', 'featured', 'created_by', 'created_on', 'downloads', 'stable', 'experimental')


class PluginVersionAdmin (admin.ModelAdmin):
    list_filter     = ('current', 'experimental', 'plugin')
    list_display    = ('plugin', 'version', 'current', 'experimental', 'created_on', 'downloads')



admin.site.register(Plugin, PluginAdmin)
admin.site.register(PluginVersion, PluginVersionAdmin)
