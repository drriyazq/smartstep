from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from content.models import Task
from notifications.models import ScheduledNotification
from rewards.models import RewardItem

from . import serializers

User = get_user_model()

DEV_USER_USERNAME = "smartstep-dev"


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def dev_token(request):
    """DEV-ONLY. Returns a JWT for a fixed dev user. Replace with real OTP flow before prod.

    The `prod` settings module should disable this view via URL wiring in a future PR
    (for now it's guarded by the DEBUG check below)."""
    from django.conf import settings

    if not settings.DEBUG:
        return Response(
            {"detail": "Dev token disabled in non-DEBUG builds."},
            status=status.HTTP_404_NOT_FOUND,
        )
    user, _ = User.objects.get_or_create(
        username=DEV_USER_USERNAME, defaults={"email": "dev@smartstep.local"}
    )
    refresh = RefreshToken.for_user(user)
    return Response({"refresh": str(refresh), "access": str(refresh.access_token)})


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def task_list(request):
    qs = Task.objects.filter(is_published=True).prefetch_related(
        "tags", "environments", "prerequisites__from_task"
    )
    environment = request.query_params.get("environment")
    if environment:
        qs = qs.filter(environments__kind=environment)
    min_age = request.query_params.get("min_age")
    max_age = request.query_params.get("max_age")
    if min_age:
        qs = qs.filter(max_age__gte=int(min_age))
    if max_age:
        qs = qs.filter(min_age__lte=int(max_age))
    tag = request.query_params.get("tag")
    if tag:
        qs = qs.filter(tags__name__iexact=tag)
    qs = qs.distinct()
    return Response(serializers.TaskSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def reward_list(request):
    qs = RewardItem.objects.filter(is_published=True).select_related("category")
    age = request.query_params.get("age")
    if age:
        age_int = int(age)
        qs = qs.filter(min_age__lte=age_int, max_age__gte=age_int)
    return Response(serializers.RewardItemSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def active_notifications(request):
    qs = ScheduledNotification.objects.filter(
        scheduled_for__lte=timezone.now(), sent_at__isnull=True
    )
    return Response(serializers.ScheduledNotificationSerializer(qs, many=True).data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def record_task_completion(request):
    """Write-only: records anonymous completion. No child identifiers accepted."""
    serializer = serializers.TaskCompletionEventSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(status=status.HTTP_201_CREATED)
