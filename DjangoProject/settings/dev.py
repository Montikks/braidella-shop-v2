from .base import *
import os

PAYMENTS_FAKE = True
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

def env_int(key, default: int):
    try:
        return int(os.getenv(key, str(default)))
    except (TypeError, ValueError):
        return int(default)

GOPAY_GOID          = env_int("GOPAY_GOID", 8123456789)
GOPAY_CLIENT_ID     = os.getenv("GOPAY_CLIENT_ID", "")
GOPAY_CLIENT_SECRET = os.getenv("GOPAY_CLIENT_SECRET", "")
GOPAY_SANDBOX       = True
