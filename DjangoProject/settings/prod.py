from .base import *
import os

DEBUG = False
ALLOWED_HOSTS = ["braidella.cz", "www.braidella.cz"]

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("SMTP_HOST", "")
EMAIL_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_HOST_USER = os.getenv("SMTP_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("SMTP_USE_TLS", "0") == "1"
EMAIL_USE_SSL = os.getenv("SMTP_USE_SSL", "0") == "1"
EMAIL_TIMEOUT = 15

DEFAULT_FROM_EMAIL = os.getenv("SHOP_FROM_EMAIL", "web@example.com")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
