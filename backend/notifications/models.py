from django.db import models


class ScheduledNotification(models.Model):
    title = models.CharField(max_length=140)
    body = models.TextField()
    scheduled_for = models.DateTimeField()
    audience_filter = models.JSONField(
        default=dict,
        blank=True,
        help_text='Opaque filter, e.g. {"environment": "urban", "age_band": "9_10"}. '
        "Delivery job interprets this against on-device state.",
    )
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scheduled_for"]

    def __str__(self) -> str:
        return f"{self.title} @ {self.scheduled_for:%Y-%m-%d %H:%M}"

    @property
    def is_sent(self) -> bool:
        return self.sent_at is not None
