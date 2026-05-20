from django.contrib import admin

from . import models


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "kind", "name", "dob", "environment", "is_active", "created_at")
    list_filter = ("kind", "environment", "is_active")
    search_fields = ("user__username", "name", "client_id")
    raw_id_fields = ("user",)


@admin.register(models.TaskProgress)
class TaskProgressAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "task_slug", "status", "repetitions_done", "completed_at")
    list_filter = ("status",)
    search_fields = ("task_slug", "profile__name")
    raw_id_fields = ("profile",)


@admin.register(models.CustomTask)
class CustomTaskAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "title", "created_at")
    search_fields = ("title", "profile__name")
    raw_id_fields = ("profile",)


@admin.register(models.CustomReward)
class CustomRewardAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "title", "is_free", "created_at")
    search_fields = ("title", "profile__name")
    raw_id_fields = ("profile",)


@admin.register(models.RewardUsage)
class RewardUsageAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "reward_category", "reward_title", "used_at")
    list_filter = ("reward_category",)
    raw_id_fields = ("profile",)


@admin.register(models.EarnedMastery)
class EarnedMasteryAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "mastery_id", "earned_at")
    search_fields = ("mastery_id", "profile__name")
    raw_id_fields = ("profile",)


@admin.register(models.SessionItem)
class SessionItemAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "key", "updated_at")
    search_fields = ("key", "profile__name")
    raw_id_fields = ("profile",)
