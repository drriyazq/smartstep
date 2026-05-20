"""Server-of-truth user data for SmartStep.

Until 2026-05-20 these tables did not exist — every profile, progress row,
custom task and reward lived only inside the user's Hive boxes. We moved the
store server-side because reinstalls + lost phones were costing users their
entire history. All seven models in this module are scoped per-user via
`profile.user`; no cross-user reads are allowed at the view layer.
"""
from django.conf import settings
from django.db import models


# ── Enums ────────────────────────────────────────────────────────────────────

class ProfileKind(models.TextChoices):
    CHILD = "child"
    ADULT = "adult"


class Sex(models.TextChoices):
    BOY = "boy"
    GIRL = "girl"
    OTHER = "other"


class Environment(models.TextChoices):
    URBAN = "urban"
    SUBURBAN = "suburban"
    RURAL = "rural"


class ProgressStatus(models.TextChoices):
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    COMPLETED = "completed"
    SKIPPED_KNOWN = "skipped_known"
    SKIPPED_UNSUITABLE = "skipped_unsuitable"
    BYPASSED = "bypassed"


# ── Profile ──────────────────────────────────────────────────────────────────

class Profile(models.Model):
    """One row per child or adult profile. A single user can hold several
    (e.g. two kids + the parent's own adult profile). Matches the Flutter
    `ChildProfile` Hive type 1:1 — `kind` discriminates child vs adult.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="userdata_profiles",
    )
    # client_id is the millisecondsSinceEpoch string the Flutter app already
    # generated when the profile was first created on-device. We keep it so
    # the client's existing `progressSlug = "custom::<id>"` etc. continues
    # to work without a remap layer.
    client_id = models.CharField(max_length=40)
    kind = models.CharField(
        max_length=8, choices=ProfileKind.choices, default=ProfileKind.CHILD
    )
    name = models.CharField(max_length=120)
    dob = models.DateField()
    sex = models.CharField(max_length=8, choices=Sex.choices)
    environment = models.CharField(max_length=12, choices=Environment.choices)

    # Legacy religion fields — feature removed from the app but the Hive
    # adapter still reads them, so we accept + store + return them for
    # round-trip fidelity with old clients. Never surfaced in the UI.
    religion_interest = models.BooleanField(default=False)
    religion = models.CharField(max_length=40, blank=True, default="")

    consent_given = models.BooleanField(default=False)
    consent_ts = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(
        default=False,
        help_text=(
            "True for the single profile the user has currently selected on "
            "this account. Only one row per user should be active; the view "
            "layer enforces this."
        ),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "client_id"], name="userdata_profile_user_client_unique"
            )
        ]
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.user.username}/{self.kind}:{self.name}"


# ── Task progress ────────────────────────────────────────────────────────────

class TaskProgress(models.Model):
    """One row per (profile, task_slug). `task_slug` is the catalog slug for
    server tasks or `custom::<custom_id>` for user-authored tasks — same
    convention the Flutter app already uses as its Hive key.
    """
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="progress"
    )
    task_slug = models.CharField(max_length=160)
    status = models.CharField(
        max_length=24,
        choices=ProgressStatus.choices,
        default=ProgressStatus.UNLOCKED,
    )
    repetitions_done = models.PositiveIntegerField(default=0)
    # Reward the user picked when claiming this task — stored alongside
    # progress because that's how the Flutter celebration sheet uses it.
    reward_title = models.CharField(max_length=200, blank=True, default="")
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "task_slug"],
                name="userdata_progress_profile_slug_unique",
            )
        ]
        indexes = [models.Index(fields=["profile", "status"])]

    def __str__(self) -> str:
        return f"{self.profile_id}:{self.task_slug}={self.status}"


# ── Custom tasks (parent-authored) ───────────────────────────────────────────

class CustomTask(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="custom_tasks"
    )
    client_id = models.CharField(max_length=40)  # millisecondsSinceEpoch from Flutter
    title = models.CharField(max_length=200)
    how_to_md = models.TextField(blank=True, default="")
    parent_note_md = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "client_id"],
                name="userdata_customtask_profile_client_unique",
            )
        ]

    @property
    def progress_slug(self) -> str:
        return f"custom::{self.client_id}"


# ── Custom rewards (parent-authored) ─────────────────────────────────────────

class CustomReward(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="custom_rewards"
    )
    client_id = models.CharField(max_length=40)
    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True, default="")
    is_free = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "client_id"],
                name="userdata_customreward_profile_client_unique",
            )
        ]


# ── Reward usage (history of redemptions) ────────────────────────────────────

class RewardUsage(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="reward_usages"
    )
    reward_category = models.CharField(max_length=80)
    reward_title = models.CharField(max_length=200)
    used_at = models.DateTimeField()

    class Meta:
        ordering = ["-used_at"]
        indexes = [models.Index(fields=["profile", "-used_at"])]


# ── Earned masteries (certificate triggers) ──────────────────────────────────

class EarnedMastery(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="masteries"
    )
    mastery_id = models.CharField(max_length=80)
    earned_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "mastery_id"],
                name="userdata_mastery_profile_id_unique",
            )
        ]


# ── Session items (catch-all for UI state) ───────────────────────────────────

class SessionItem(models.Model):
    """Key-value bucket for everything the old `sessionBox` held that isn't
    JWT/auth (those stay in flutter_secure_storage). Examples:
    - `filter::<category>` → bool, whether the chip is enabled
    - `collapsed::<category>` → bool, whether the Done section is collapsed
    - `todays_pick` → JSON array of task slugs picked for today
    Scoping is per-profile because filter chips can differ between a child
    and the parent's adult profile on the same account.
    """
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="session_items"
    )
    key = models.CharField(max_length=160)
    value = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "key"],
                name="userdata_sessionitem_profile_key_unique",
            )
        ]
