from plugins.models import Plugin, PluginVersion #, PluginCrashReport
from django.contrib.gis import admin


class PluginAdmin (admin.ModelAdmin):
    list_filter     = ('featured',)
    list_display    = ('name', 'featured', 'created_by', 'created_on', 'downloads', 'stable', 'experimental')
    search_fields   = ('name',)


class PluginVersionAdmin (admin.ModelAdmin):
    list_filter     = ('experimental', 'approved', 'plugin')
    list_display    = ('plugin', 'approved', 'version', 'experimental', 'created_on', 'downloads')


#class PluginCrashReportAdmin(admin.ModelAdmin):
    #pass


admin.site.register(Plugin, PluginAdmin)
admin.site.register(PluginVersion, PluginVersionAdmin)
#admin.site.register(PluginCrashReport, PluginCrashReportAdmin)
