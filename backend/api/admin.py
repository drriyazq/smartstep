from django.contrib import admin

from .models import AppUserPhone, OtpDeliveryLog


@admin.register(AppUserPhone)
class AppUserPhoneAdmin(admin.ModelAdmin):
    list_display = ("phone_e164", "user", "verified_at", "created_at")
    search_fields = ("phone_e164", "user__username", "user__email")
    list_filter = ("verified_at",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("user",)
    list_select_related = ("user",)


@admin.register(OtpDeliveryLog)
class OtpDeliveryLogAdmin(admin.ModelAdmin):
    list_display = ("phone", "result_ok", "template_name", "created_at", "message_id")
    list_filter = ("result_ok", "template_name", "created_at")
    search_fields = ("phone", "message_id", "error_message")
    readonly_fields = (
        "phone",
        "template_name",
        "result_ok",
        "message_id",
        "error_message",
        "response_json",
        "created_at",
    )
