from django.contrib import admin
from models.models import Model, ModelReview


class ModelInline(admin.TabularInline):
    model = ModelReview
    list_display = ('review_date', 'comment', 'reviewer')


@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    inlines = [ModelInline, ]
    list_display = ('name', 'description', 'creator', 'upload_date',)
    search_fields = ('name', 'description',)


@admin.register(ModelReview)
class ModelReviewAdmin(admin.ModelAdmin):
    list_display = ('model', 'reviewer', 'comment', 'review_date',)
