from django.contrib import admin

from base.models import SitePreference
from wavefronts.models import Wavefront, Review

# django-preferences
from preferences.admin import PreferencesAdmin
from wavefronts.models import FilesizePreferences


class WavefrontInline(admin.TabularInline):
    model = Review
    list_display = ('review_date', 'comment', 'reviewer')


@admin.register(Wavefront)
class WavefrontAdmin(admin.ModelAdmin):
    inlines = [WavefrontInline, ]
    list_display = ('name', 'description', 'creator', 'upload_date',)
    search_fields = ('name', 'description',)


@admin.register(Review)
class WavefrontReviewAdmin(admin.ModelAdmin):
    list_display = ('resource', 'reviewer', 'comment', 'review_date',)


# django-preferences
admin.site.register(FilesizePreferences, PreferencesAdmin)
admin.site.register(SitePreference, PreferencesAdmin)
