import logging
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from content.models import ReviewStatus, Task
from notifications.models import ScheduledNotification
from rewards.models import RewardItem

from . import otp as otp_store
from . import serializers
from . import whatsapp as wa
from .models import AppUserPhone, OtpDeliveryLog

logger = logging.getLogger(__name__)

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
    qs = Task.objects.filter(status=ReviewStatus.APPROVED).prefetch_related(
        "tags", "environments", "prerequisites__from_task"
    )
    environment = request.query_params.get("environment")
    if environment:
        qs = qs.filter(environments__kind=environment)
    sex = request.query_params.get("sex")
    if sex and sex != "any":
        qs = qs.filter(sex_filter__in=["any", sex])
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
    qs = RewardItem.objects.filter(status=ReviewStatus.APPROVED).select_related("category")
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


def _normalize_e164(raw: str) -> str:
    """Strip whitespace/dashes/parens; keep the leading +. Returns '' if the
    result doesn't look like an E.164 number (8-15 digits after the +)."""
    if not raw:
        return ""
    cleaned = re.sub(r"[\s\-\(\)]", "", raw.strip())
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
    if not cleaned.startswith("+"):
        return ""
    digits = cleaned[1:]
    if not digits.isdigit() or not (8 <= len(digits) <= 15):
        return ""
    return cleaned


def _issue_jwt_for_phone(phone: str):
    """Find or create the Django user attached to an E.164 phone, then return
    a JWT pair. Existing accounts get reused via `AppUserPhone.phone_e164`;
    new accounts land at `username=phone_<E164-no-plus>`.
    """
    link = AppUserPhone.objects.filter(phone_e164=phone).select_related("user").first()
    if link:
        user = link.user
        link.verified_at = timezone.now()
        link.save(update_fields=["verified_at"])
    else:
        with transaction.atomic():
            stripped = phone.lstrip("+")
            user, _ = User.objects.get_or_create(
                username=f"phone_{stripped}",
                defaults={"email": f"{stripped}@smartstep.phone"},
            )
            AppUserPhone.objects.create(
                user=user,
                phone_e164=phone,
                verified_at=timezone.now(),
            )
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "uid": phone,
    }


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def send_otp(request):
    """Generate a 6-digit OTP and send it via WhatsApp template.

    Body: {"phone": "+919867933139"}
    Returns 204 on success (never echo the code).
    Test bypass: numbers in OTP_TEST_PHONES skip the WhatsApp send entirely.
    """
    phone = _normalize_e164(request.data.get("phone", ""))
    if not phone:
        return Response(
            {"detail": "Valid phone (E.164, e.g. +919876543210) required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if phone in settings.OTP_TEST_PHONES:
        # No code stored; verify_otp accepts OTP_TEST_CODE directly.
        return Response(status=status.HTTP_204_NO_CONTENT)

    code = otp_store.generate_code()
    otp_store.store(phone, code)

    result = wa.send_otp_template(phone, code)
    OtpDeliveryLog.objects.create(
        phone=phone,
        template_name=settings.WHATSAPP_OTP_TEMPLATE_NAME,
        result_ok=result.get("ok", False),
        message_id=result.get("message_id", ""),
        error_message=(result.get("error") or "")[:2000],
        response_json=result.get("response", {}),
    )

    if not result.get("ok"):
        logger.warning("[otp] WhatsApp send failed for %s: %s", phone, result.get("error"))
        return Response(
            {"detail": "Could not send OTP. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def verify_otp(request):
    """Verify an OTP and return a SimpleJWT pair plus E.164 uid.

    Body: {"phone": "+919867933139", "code": "123456"}
    Response: {"refresh": "...", "access": "...", "uid": "+91…"}
    """
    phone = _normalize_e164(request.data.get("phone", ""))
    code = (request.data.get("code") or "").strip()
    if not phone or not code:
        return Response(
            {"detail": "phone and code required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    test_bypass = (
        phone in settings.OTP_TEST_PHONES
        and settings.OTP_TEST_CODE
        and code == settings.OTP_TEST_CODE
    )
    if not test_bypass:
        result = otp_store.verify(phone, code)
        if result == otp_store.VerifyResult.WRONG_CODE:
            return Response({"detail": "Incorrect code."}, status=status.HTTP_400_BAD_REQUEST)
        if result == otp_store.VerifyResult.EXPIRED:
            return Response(
                {"detail": "Code expired. Request a new OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if result == otp_store.VerifyResult.TOO_MANY_ATTEMPTS:
            return Response(
                {"detail": "Too many wrong attempts. Request a new OTP."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        # else: VerifyResult.OK — fall through

    return Response(_issue_jwt_for_phone(phone))


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def firebase_auth(request):
    """Verify a Firebase Phone Auth ID token (non-+91 fallback) and return a
    Django JWT pair. If Firebase reports a phone number on the token, that
    phone is also linked via `AppUserPhone` so the same account can later be
    matched from the WhatsApp OTP path.
    """
    import firebase_admin
    from firebase_admin import auth as fb_auth, credentials

    id_token = request.data.get("id_token", "").strip()
    if not id_token:
        return Response({"detail": "id_token required."}, status=status.HTTP_400_BAD_REQUEST)

    if not firebase_admin._apps:
        cred = credentials.Certificate(str(settings.FIREBASE_CREDENTIALS_PATH))
        firebase_admin.initialize_app(cred)

    try:
        decoded = fb_auth.verify_id_token(id_token)
    except Exception:
        return Response(
            {"detail": "Invalid or expired Firebase token."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    fb_phone = _normalize_e164(decoded.get("phone_number", "") or "")
    if fb_phone:
        # Re-claim a pre-existing account by phone if one exists.
        link = AppUserPhone.objects.filter(phone_e164=fb_phone).select_related("user").first()
        if link:
            link.verified_at = timezone.now()
            link.save(update_fields=["verified_at"])
            refresh = RefreshToken.for_user(link.user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "uid": fb_phone,
            })

    uid = decoded["uid"]
    user, _ = User.objects.get_or_create(
        username=f"firebase_{uid}",
        defaults={"email": f"{uid}@smartstep.firebase"},
    )
    if fb_phone:
        AppUserPhone.objects.update_or_create(
            user=user,
            defaults={"phone_e164": fb_phone, "verified_at": timezone.now()},
        )

    refresh = RefreshToken.for_user(user)
    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "uid": fb_phone or uid,
    })
