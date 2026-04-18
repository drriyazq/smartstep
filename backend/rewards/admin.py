from django.contrib import admin, messages
from django.utils.html import format_html

from content.models import ReviewStatus

from .models import RewardCategory, RewardItem


STATUS_COLORS = {
    ReviewStatus.DRAFT: "#9ca3af",
    ReviewStatus.PENDING: "#f59e0b",
    ReviewStatus.APPROVED: "#10b981",
    ReviewStatus.REJECTED: "#ef4444",
}


def _status_badge(status_value: str) -> str:
    label = dict(ReviewStatus.choices).get(status_value, status_value)
    color = STATUS_COLORS.get(status_value, "#6b7280")
    return format_html(
        '<span style="background:{};color:white;padding:2px 8px;'
        'border-radius:10px;font-size:11px;font-weight:600;">{}</span>',
        color,
        label,
    )


@admin.register(RewardCategory)
class RewardCategoryAdmin(admin.ModelAdmin):
    list_display = ("kind", "display_name")


@admin.register(RewardItem)
class RewardItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status_badge", "min_age", "max_age", "is_free")
    list_filter = ("status", "category", "is_free")
    search_fields = ("title", "notes")
    actions = [
        "approve_rewards",
        "reject_rewards",
        "submit_for_review",
        "send_back_to_draft",
    ]
    fieldsets = (
        (None, {"fields": ("title", "category", "status", "review_notes")}),
        ("Audience", {"fields": ("min_age", "max_age", "is_free", "notes")}),
    )

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        return _status_badge(obj.status)

    @admin.action(description="✓ Approve (publish to app)")
    def approve_rewards(self, request, queryset):
        count = queryset.update(status=ReviewStatus.APPROVED)
        self.message_user(request, f"Approved {count} reward(s).", messages.SUCCESS)

    @admin.action(description="✗ Reject")
    def reject_rewards(self, request, queryset):
        count = queryset.update(status=ReviewStatus.REJECTED)
        self.message_user(request, f"Rejected {count} reward(s).", messages.WARNING)

    @admin.action(description="→ Submit for review")
    def submit_for_review(self, request, queryset):
        count = queryset.update(status=ReviewStatus.PENDING)
        self.message_user(request, f"Moved {count} reward(s) to pending review.", messages.INFO)

    @admin.action(description="← Send back to draft")
    def send_back_to_draft(self, request, queryset):
        count = queryset.update(status=ReviewStatus.DRAFT)
        self.message_user(request, f"Moved {count} reward(s) back to draft.", messages.INFO)
