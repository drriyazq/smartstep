"""Auth-side models for SmartStep.

Server holds nothing about the child — these models only support the phone-based
login flow. PII boundary is documented in the top-level CLAUDE.md.
"""
from django.contrib.auth.models import User
from django.db import models


class AppUserPhone(models.Model):
    """Maps a Django `User` to an E.164 phone number.

    Lookup target for WhatsApp / Firebase Phone Auth so existing accounts
    (originally `firebase_<google_uid>`) can be re-claimed by their owner
    after the Google Sign-In path was removed. The username on the User row
    stays as-is; only this side table moves.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="phone_link"
    )
    phone_e164 = models.CharField(max_length=20, unique=True, db_index=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.user.username} → {self.phone_e164}"


class OtpDeliveryLog(models.Model):
    """Audit row for every WhatsApp OTP send attempt. Use this to debug
    deliverability issues (template rejected, token expired, phone-id wrong) —
    Meta's full error payload lands in `response_json`.
    """
    phone = models.CharField(max_length=20, db_index=True)
    template_name = models.CharField(max_length=100)
    result_ok = models.BooleanField(default=False)
    message_id = models.CharField(max_length=200, blank=True)
    error_message = models.TextField(blank=True)
    response_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.phone} {'OK' if self.result_ok else 'FAIL'} {self.created_at:%Y-%m-%d %H:%M}"
