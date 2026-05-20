"""Views for /api/v1/me/.

Cross-user safety pattern: every ViewSet's `get_queryset()` is filtered on
`profile__user=self.request.user` (or `user=self.request.user` for Profile
itself), and `perform_create()` validates that any `profile` parent FK
belongs to the requesting user. There is no admin-style "scope expander" —
a user can only ever see / write their own data.

Upsert pattern: most resources are keyed by `(profile, client_id)` or
`(profile, task_slug)` so the Flutter app can blindly PUT without first
checking whether a row exists. We expose `/upsert/` collection actions for
this — DRF's default PUT on detail requires the pk, which the client doesn't
necessarily have when it just generated a millisecondsSinceEpoch id locally.
"""
from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, serializers


# ── Base helpers ─────────────────────────────────────────────────────────────

class _OwnedViewSet(viewsets.ModelViewSet):
    """Restricts both reads and writes to the requesting user. Subclasses
    set `owner_path` to the dotted lookup that reaches `auth.User`."""
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # /me/ payloads are bounded per-user, paging is noise
    owner_path = "profile__user"

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(**{self.owner_path: self.request.user})

    def _assert_profile_owned(self, profile):
        if profile.user_id != self.request.user.id:
            raise PermissionError("Profile does not belong to the requesting user.")


# ── Profiles ─────────────────────────────────────────────────────────────────

class ProfileViewSet(_OwnedViewSet):
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    owner_path = "user"

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], url_path="upsert")
    def upsert(self, request):
        """POST/PUT a profile keyed by client_id (the millisecondsSinceEpoch
        string Flutter generated on-device). Idempotent on retries — no
        duplicate rows even if the network drops between request and ack.
        """
        client_id = request.data.get("client_id")
        if not client_id:
            return Response(
                {"detail": "client_id required."}, status=status.HTTP_400_BAD_REQUEST
            )
        instance = models.Profile.objects.filter(
            user=request.user, client_id=client_id
        ).first()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="activate")
    def activate(self, request, pk=None):
        """Mark this profile as the active one for the user. Atomic flip:
        clears `is_active` on every other profile in a single transaction so
        the unique-active invariant is never visibly broken."""
        profile = self.get_object()
        with transaction.atomic():
            models.Profile.objects.filter(user=request.user, is_active=True).update(
                is_active=False
            )
            profile.is_active = True
            profile.save(update_fields=["is_active", "updated_at"])
        return Response(self.get_serializer(profile).data)

    @action(detail=True, methods=["post"], url_path="reset-progress")
    def reset_progress(self, request, pk=None):
        """Wipes every TaskProgress + RewardUsage + EarnedMastery row for
        this profile. The profile row itself stays, as do custom tasks and
        custom rewards. Used by the "Reset all progress" button on the
        profile screen."""
        profile = self.get_object()
        with transaction.atomic():
            deleted_progress, _ = models.TaskProgress.objects.filter(
                profile=profile
            ).delete()
            deleted_usage, _ = models.RewardUsage.objects.filter(
                profile=profile
            ).delete()
            deleted_mastery, _ = models.EarnedMastery.objects.filter(
                profile=profile
            ).delete()
        return Response(
            {
                "progress_rows_deleted": deleted_progress,
                "reward_usages_deleted": deleted_usage,
                "masteries_deleted": deleted_mastery,
            }
        )


# ── Task progress ────────────────────────────────────────────────────────────

class TaskProgressViewSet(_OwnedViewSet):
    queryset = models.TaskProgress.objects.select_related("profile")
    serializer_class = serializers.TaskProgressSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        profile_id = self.request.query_params.get("profile")
        if profile_id:
            qs = qs.filter(profile_id=profile_id)
        return qs

    def perform_create(self, serializer):
        profile = serializer.validated_data["profile"]
        self._assert_profile_owned(profile)
        serializer.save()

    @action(detail=False, methods=["post"], url_path="upsert")
    def upsert(self, request):
        """Upsert by (profile, task_slug). The Flutter app calls this on
        every progress change because it never knows the row's pk."""
        profile_id = request.data.get("profile")
        task_slug = request.data.get("task_slug")
        if not profile_id or not task_slug:
            return Response(
                {"detail": "profile and task_slug required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile = models.Profile.objects.filter(
            id=profile_id, user=request.user
        ).first()
        if not profile:
            return Response(
                {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
            )
        instance = models.TaskProgress.objects.filter(
            profile=profile, task_slug=task_slug
        ).first()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


# ── Custom tasks ─────────────────────────────────────────────────────────────

class CustomTaskViewSet(_OwnedViewSet):
    queryset = models.CustomTask.objects.select_related("profile")
    serializer_class = serializers.CustomTaskSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        profile_id = self.request.query_params.get("profile")
        if profile_id:
            qs = qs.filter(profile_id=profile_id)
        return qs

    def perform_create(self, serializer):
        profile = serializer.validated_data["profile"]
        self._assert_profile_owned(profile)
        serializer.save()

    @action(detail=False, methods=["post"], url_path="upsert")
    def upsert(self, request):
        profile_id = request.data.get("profile")
        client_id = request.data.get("client_id")
        if not profile_id or not client_id:
            return Response(
                {"detail": "profile and client_id required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile = models.Profile.objects.filter(
            id=profile_id, user=request.user
        ).first()
        if not profile:
            return Response(
                {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
            )
        instance = models.CustomTask.objects.filter(
            profile=profile, client_id=client_id
        ).first()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


# ── Custom rewards ───────────────────────────────────────────────────────────

class CustomRewardViewSet(_OwnedViewSet):
    queryset = models.CustomReward.objects.select_related("profile")
    serializer_class = serializers.CustomRewardSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        profile_id = self.request.query_params.get("profile")
        if profile_id:
            qs = qs.filter(profile_id=profile_id)
        return qs

    def perform_create(self, serializer):
        profile = serializer.validated_data["profile"]
        self._assert_profile_owned(profile)
        serializer.save()

    @action(detail=False, methods=["post"], url_path="upsert")
    def upsert(self, request):
        profile_id = request.data.get("profile")
        client_id = request.data.get("client_id")
        if not profile_id or not client_id:
            return Response(
                {"detail": "profile and client_id required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile = models.Profile.objects.filter(
            id=profile_id, user=request.user
        ).first()
        if not profile:
            return Response(
                {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
            )
        instance = models.CustomReward.objects.filter(
            profile=profile, client_id=client_id
        ).first()
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


# ── Reward usage ─────────────────────────────────────────────────────────────

class RewardUsageViewSet(_OwnedViewSet):
    queryset = models.RewardUsage.objects.select_related("profile")
    serializer_class = serializers.RewardUsageSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        profile_id = self.request.query_params.get("profile")
        if profile_id:
            qs = qs.filter(profile_id=profile_id)
        return qs

    def perform_create(self, serializer):
        profile = serializer.validated_data["profile"]
        self._assert_profile_owned(profile)
        serializer.save()


# ── Earned masteries ─────────────────────────────────────────────────────────

class EarnedMasteryViewSet(_OwnedViewSet):
    queryset = models.EarnedMastery.objects.select_related("profile")
    serializer_class = serializers.EarnedMasterySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        profile_id = self.request.query_params.get("profile")
        if profile_id:
            qs = qs.filter(profile_id=profile_id)
        return qs

    def perform_create(self, serializer):
        profile = serializer.validated_data["profile"]
        self._assert_profile_owned(profile)
        serializer.save()

    @action(detail=False, methods=["post"], url_path="claim")
    def claim(self, request):
        """Idempotent — re-claiming an already-earned mastery returns the
        existing row instead of 409. Earned masteries are append-only;
        we never delete them."""
        profile_id = request.data.get("profile")
        mastery_id = request.data.get("mastery_id")
        earned_at = request.data.get("earned_at")
        if not (profile_id and mastery_id and earned_at):
            return Response(
                {"detail": "profile, mastery_id, earned_at required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile = models.Profile.objects.filter(
            id=profile_id, user=request.user
        ).first()
        if not profile:
            return Response(
                {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
            )
        obj, _created = models.EarnedMastery.objects.get_or_create(
            profile=profile,
            mastery_id=mastery_id,
            defaults={"earned_at": earned_at},
        )
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


# ── Session items ────────────────────────────────────────────────────────────

class SessionItemViewSet(_OwnedViewSet):
    queryset = models.SessionItem.objects.select_related("profile")
    serializer_class = serializers.SessionItemSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        profile_id = self.request.query_params.get("profile")
        if profile_id:
            qs = qs.filter(profile_id=profile_id)
        return qs

    def perform_create(self, serializer):
        profile = serializer.validated_data["profile"]
        self._assert_profile_owned(profile)
        serializer.save()

    @action(detail=False, methods=["post"], url_path="upsert")
    def upsert(self, request):
        """Upsert by (profile, key). Body: {profile, key, value}."""
        profile_id = request.data.get("profile")
        key = request.data.get("key")
        value = request.data.get("value", {})
        if not profile_id or not key:
            return Response(
                {"detail": "profile and key required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        profile = models.Profile.objects.filter(
            id=profile_id, user=request.user
        ).first()
        if not profile:
            return Response(
                {"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
            )
        obj, _ = models.SessionItem.objects.update_or_create(
            profile=profile, key=key, defaults={"value": value}
        )
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


# ── Bulk state hydrator ──────────────────────────────────────────────────────

class BulkStateView(APIView):
    """GET /api/v1/me/state/ — single round-trip pull of everything the
    Flutter app needs to populate its in-memory cache on cold start."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profiles = models.Profile.objects.filter(user=user)
        profile_ids = list(profiles.values_list("id", flat=True))

        payload = {
            "profiles": serializers.ProfileSerializer(profiles, many=True).data,
            "progress": serializers.TaskProgressSerializer(
                models.TaskProgress.objects.filter(profile_id__in=profile_ids),
                many=True,
            ).data,
            "custom_tasks": serializers.CustomTaskSerializer(
                models.CustomTask.objects.filter(profile_id__in=profile_ids),
                many=True,
            ).data,
            "custom_rewards": serializers.CustomRewardSerializer(
                models.CustomReward.objects.filter(profile_id__in=profile_ids),
                many=True,
            ).data,
            "reward_usages": serializers.RewardUsageSerializer(
                models.RewardUsage.objects.filter(profile_id__in=profile_ids),
                many=True,
            ).data,
            "masteries": serializers.EarnedMasterySerializer(
                models.EarnedMastery.objects.filter(profile_id__in=profile_ids),
                many=True,
            ).data,
            "session_items": serializers.SessionItemSerializer(
                models.SessionItem.objects.filter(profile_id__in=profile_ids),
                many=True,
            ).data,
        }
        return Response(payload)


class WipeView(APIView):
    """DELETE /api/v1/me/wipe/ — DPDP-mandated delete. Cascades through
    every profile this user owns; the user's auth row itself is NOT touched
    (they can re-onboard with the same phone if they choose to)."""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        deleted, _ = models.Profile.objects.filter(user=request.user).delete()
        return Response({"deleted_rows": deleted}, status=status.HTTP_200_OK)
