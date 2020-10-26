from django.contrib import admin
from .models import Resource, ResourceType


class ResourceTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'order')
    list_editable = ('order',)


class ResourceAdmin(admin.ModelAdmin):
    list_display = ('name',
                    'description',
                    'creator',
                    'upload_date',
                    'get_resource_types')


admin.site.register(Resource, ResourceAdmin)
admin.site.register(ResourceType, ResourceTypeAdmin)
