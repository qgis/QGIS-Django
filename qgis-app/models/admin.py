from django.contrib import admin
from models.models import Model, Review


class ModelInline(admin.TabularInline):
    model = Review
    list_display = ("review_date", "comment", "reviewer")


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    inlines = [
        ModelInline,
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
class ModelReviewAdmin(admin.ModelAdmin):
    list_display = (
        "resource",
        "reviewer",
        "comment",
        "review_date",
    )
