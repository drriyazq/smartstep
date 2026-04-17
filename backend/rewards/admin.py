from django.contrib import admin

from .models import RewardCategory, RewardItem


@admin.register(RewardCategory)
class RewardCategoryAdmin(admin.ModelAdmin):
    list_display = ("kind", "display_name")


@admin.register(RewardItem)
class RewardItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "min_age", "max_age", "is_free", "is_published")
    list_filter = ("category", "is_free", "is_published")
    search_fields = ("title", "notes")
