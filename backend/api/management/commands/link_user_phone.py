"""Link a Django user to an E.164 phone number so they can sign in via OTP.

Two modes:

  Single:
    python manage.py link_user_phone <username_or_email> +919876543210

  Batch from CSV (`username_or_email,phone_e164` per row, skips header if
  the first field is literally `username_or_email`):
    python manage.py link_user_phone --csv path/to/users.csv

Idempotent: re-running with the same pairing updates the AppUserPhone row
and sets `verified_at=now`. Raises if the phone is already attached to a
different user (you must clear the conflict manually).
"""
import csv
import re
import sys

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from api.models import AppUserPhone

User = get_user_model()


def _normalize_e164(raw: str) -> str:
    cleaned = re.sub(r"[\s\-\(\)]", "", raw.strip())
    if cleaned.startswith("00"):
        cleaned = "+" + cleaned[2:]
    if not cleaned.startswith("+"):
        return ""
    digits = cleaned[1:]
    if not digits.isdigit() or not (8 <= len(digits) <= 15):
        return ""
    return cleaned


def _resolve_user(identifier: str):
    identifier = identifier.strip()
    user = User.objects.filter(username=identifier).first()
    if user:
        return user
    user = User.objects.filter(email__iexact=identifier).first()
    if user:
        return user
    return None


class Command(BaseCommand):
    help = "Link a Django user to a phone (E.164) for OTP login."

    def add_arguments(self, parser):
        parser.add_argument("identifier", nargs="?", help="username or email")
        parser.add_argument("phone", nargs="?", help="phone in E.164, e.g. +919876543210")
        parser.add_argument("--csv", dest="csv_path", help="batch CSV (identifier,phone per row)")

    def handle(self, *args, **opts):
        if opts["csv_path"]:
            self._handle_csv(opts["csv_path"])
            return

        if not opts["identifier"] or not opts["phone"]:
            raise CommandError(
                "Provide <identifier> <phone> or --csv. See `link_user_phone --help`."
            )
        ok = self._link_one(opts["identifier"], opts["phone"])
        sys.exit(0 if ok else 1)

    def _handle_csv(self, path: str):
        ok_count = 0
        fail_count = 0
        with open(path, newline="") as f:
            reader = csv.reader(f)
            for row_num, row in enumerate(reader, 1):
                if not row or len(row) < 2:
                    continue
                identifier, phone = row[0], row[1]
                if row_num == 1 and identifier.strip().lower() in {
                    "username_or_email", "username", "email", "identifier"
                }:
                    continue  # skip header
                if self._link_one(identifier, phone):
                    ok_count += 1
                else:
                    fail_count += 1
        self.stdout.write(self.style.SUCCESS(f"Linked: {ok_count}"))
        if fail_count:
            self.stdout.write(self.style.WARNING(f"Failed: {fail_count}"))

    def _link_one(self, identifier: str, phone_raw: str) -> bool:
        phone = _normalize_e164(phone_raw)
        if not phone:
            self.stderr.write(f"  invalid phone {phone_raw!r} for {identifier}")
            return False
        user = _resolve_user(identifier)
        if not user:
            self.stderr.write(f"  no user for {identifier!r}")
            return False
        # Reject if the phone is already taken by someone else.
        existing = AppUserPhone.objects.filter(phone_e164=phone).select_related("user").first()
        if existing and existing.user_id != user.id:
            self.stderr.write(
                f"  phone {phone} already linked to {existing.user.username}"
                f" — skipping {identifier}"
            )
            return False
        with transaction.atomic():
            link, created = AppUserPhone.objects.update_or_create(
                user=user,
                defaults={"phone_e164": phone, "verified_at": timezone.now()},
            )
        verb = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"  {verb} {user.username} → {phone}"))
        return True
