import os

from .base import *  # noqa: F401, F403

DEBUG = True
ALLOWED_HOSTS = ["*"]
CORS_ALLOW_ALL_ORIGINS = True
FORCE_SCRIPT_NAME = "/smartstep-admin"
CSRF_TRUSTED_ORIGINS = ["https://areafair.in", "https://www.areafair.in"]
