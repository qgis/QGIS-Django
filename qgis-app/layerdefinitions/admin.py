from django.contrib import admin
from layerdefinitions.models import LayerDefinition, Review


class LayerDefinitionInline(admin.TabularInline):
    model = Review
    list_display = ("review_date", "comment", "reviewer")


@admin.register(LayerDefinition)
class LayerDefinitionAdmin(admin.ModelAdmin):
    inlines = [
        LayerDefinitionInline,
    ]
    list_display = (
        "name",
        "description",
        "creator",
        "upload_date",
    )
    search_fields = ("name", "description", "provider")


@admin.register(Review)
class LayerDefinitionReviewAdmin(admin.ModelAdmin):
    list_display = (
        "resource",
        "reviewer",
        "comment",
        "review_date",
    )
