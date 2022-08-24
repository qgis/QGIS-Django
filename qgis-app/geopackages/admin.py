from django.contrib import admin
from geopackages.models import Geopackage, Review


class GeopackageInline(admin.TabularInline):
    model = Review
    list_display = ("review_date", "comment", "reviewer")


@admin.register(Geopackage)
class GeopackageAdmin(admin.ModelAdmin):
    inlines = [
        GeopackageInline,
    ]
    list_display = (
        "name",
        "description",
        "creator",
        "upload_date",
    )
    search_fields = (
        "name",
        "description",
    )


@admin.register(Review)
class GeopackageReviewAdmin(admin.ModelAdmin):
    list_display = (
        "resource",
        "reviewer",
        "comment",
        "review_date",
    )
