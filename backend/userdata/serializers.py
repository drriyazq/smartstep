"""Serializers for the /api/v1/me/ tree. Every payload is scoped to one user
via the view layer (`get_queryset` filters on `request.user`), so these
serializers don't need to re-check ownership — they just shape the JSON.
"""
from rest_framework import serializers

from . import models


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = (
            "id",
            "client_id",
            "kind",
            "name",
            "dob",
            "sex",
            "environment",
            "religion_interest",
            "religion",
            "consent_given",
            "consent_ts",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class TaskProgressSerializer(serializers.ModelSerializer):
    # We always look up by (profile, task_slug) on writes, never by row id.
    # Including profile_client_id lets the Flutter app keep its existing
    # progressBox key `<childId>::<taskSlug>` without an id mapping table.
    profile_client_id = serializers.CharField(
        source="profile.client_id", read_only=True
    )

    class Meta:
        model = models.TaskProgress
        fields = (
            "id",
            "profile",
            "profile_client_id",
            "task_slug",
            "status",
            "repetitions_done",
            "reward_title",
            "completed_at",
            "updated_at",
        )
        read_only_fields = ("id", "updated_at", "profile_client_id")


class CustomTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomTask
        fields = (
            "id",
            "profile",
            "client_id",
            "title",
            "how_to_md",
            "parent_note_md",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class CustomRewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CustomReward
        fields = (
            "id",
            "profile",
            "client_id",
            "title",
            "notes",
            "is_free",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class RewardUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RewardUsage
        fields = ("id", "profile", "reward_category", "reward_title", "used_at")
        read_only_fields = ("id",)


class EarnedMasterySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.EarnedMastery
        fields = ("id", "profile", "mastery_id", "earned_at")
        read_only_fields = ("id",)


class SessionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SessionItem
        fields = ("id", "profile", "key", "value", "updated_at")
        read_only_fields = ("id", "updated_at")


class BulkStateSerializer(serializers.Serializer):
    """The shape returned by GET /api/v1/me/state/. The Flutter app calls
    this on every cold start to hydrate its in-memory cache in one round-trip
    instead of 7 sequential requests.
    """
    profiles = ProfileSerializer(many=True)
    progress = TaskProgressSerializer(many=True)
    custom_tasks = CustomTaskSerializer(many=True)
    custom_rewards = CustomRewardSerializer(many=True)
    reward_usages = RewardUsageSerializer(many=True)
    masteries = EarnedMasterySerializer(many=True)
    session_items = SessionItemSerializer(many=True)
