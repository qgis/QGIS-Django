from django.contrib import admin
from geopackages.models import Geopackage, GeopackageReview


class GeopackageInline(admin.TabularInline):
    model = GeopackageReview
    list_display = ('review_date', 'comment', 'reviewer')


@admin.register(Geopackage)
class GeopackageAdmin(admin.ModelAdmin):
    inlines = [GeopackageInline, ]
    list_display = ('name', 'description', 'creator', 'upload_date',)
    search_fields = ('name', 'description',)


@admin.register(GeopackageReview)
class GeopackageReviewAdmin(admin.ModelAdmin):
    list_display = ('geopackage', 'reviewer', 'comment', 'review_date',)
