from django.contrib import admin

from .models import ScheduledNotification


@admin.register(ScheduledNotification)
class ScheduledNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "scheduled_for", "is_sent")
    list_filter = ("scheduled_for",)
    search_fields = ("title", "body")
    readonly_fields = ("sent_at", "created_at")
