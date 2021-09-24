from django.contrib import admin
from wavefronts.models import Wavefront, Review


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
