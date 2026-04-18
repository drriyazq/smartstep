"""Non-interactive admin password reset. Django ships `changepassword` but it
prompts — this one takes --username and --password as args so it works in
deploy scripts and docker entrypoints."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or reset a Django admin user non-interactively."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--email", default="")

    def handle(self, *args, username, password, email, **options):
        if len(password) < 8:
            raise CommandError("Password must be at least 8 characters.")
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username=username, defaults={"email": email, "is_staff": True, "is_superuser": True}
        )
        user.is_staff = True
        user.is_superuser = True
        if email and user.email != email:
            user.email = email
        user.set_password(password)
        user.save()
        verb = "Created" if created else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} superuser '{username}'."))
