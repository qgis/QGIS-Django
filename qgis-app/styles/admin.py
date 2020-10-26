from django.contrib import admin
from .models import Style, StyleType


class StyleTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'order')
    list_editable = ('order',)


class StyleAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'description',
                    'creator',
                    'upload_date',
                    'get_style_types')


admin.site.register(Style, StyleAdmin)
admin.site.register(StyleType, StyleTypeAdmin)
