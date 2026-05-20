from django.apps import AppConfig


class UserdataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "userdata"
    verbose_name = "User Data (server-of-truth)"
