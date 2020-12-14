from django.contrib import admin
from modelers.models import Modeler, ModelerReview


class ModelerInline(admin.TabularInline):
    model = ModelerReview
    list_display = ('review_date', 'comment', 'reviewer')


@admin.register(Modeler)
class ModelerAdmin(admin.ModelAdmin):
    inlines = [ModelerInline, ]
    list_display = ('name', 'description', 'creator', 'upload_date',)
    search_fields = ('name', 'description',)


@admin.register(ModelerReview)
class ModelerReviewAdmin(admin.ModelAdmin):
    list_display = ('modeler', 'reviewer', 'comment', 'review_date',)
