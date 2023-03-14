from django.contrib import admin
from plugins.models import (
    Plugin, PluginVersion,
    PluginLegacyName# , PluginCrashReport
)


class PluginAdmin(admin.ModelAdmin):
    list_filter = ("featured",)
    list_display = (
        "name",
        "featured",
        "created_by",
        "created_on",
        "downloads",
        "stable",
        "experimental",
    )
    search_fields = ("name",)


class PluginVersionAdmin(admin.ModelAdmin):
    list_filter = ("experimental", "approved", "plugin")
    list_display = (
        "plugin",
        "approved",
        "version",
        "experimental",
        "created_on",
        "downloads",
    )
    search_fields = (
        'plugin__name',
    )


# class PluginCrashReportAdmin(admin.ModelAdmin):
# pass


class PluginLegacyNameAdmin(admin.ModelAdmin):
    list_display = (
        'plugin',
        'package_name',
        'created_on'
    )
    readonly_fields = (
        'created_on',
        'package_name'
    )


admin.site.register(Plugin, PluginAdmin)
admin.site.register(PluginVersion, PluginVersionAdmin)
admin.site.register(PluginLegacyName, PluginLegacyNameAdmin)
# admin.site.register(PluginCrashReport, PluginCrashReportAdmin)
