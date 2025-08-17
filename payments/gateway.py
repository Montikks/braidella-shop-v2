import gopay
from django.conf import settings

# Fallback na nové/ staré SDK – novější vyžaduje text "payment-all"
try:
    from gopay.enums import Scope
    SCOPE_ALL = getattr(Scope, "ALL", "payment-all")
except Exception:
    SCOPE_ALL = "payment-all"

def gopay_client():
    return gopay.payments(
        {
            "goid":         settings.GOPAY_GOID,
            "clientId":     settings.GOPAY_CLIENT_ID,
            "clientSecret": settings.GOPAY_CLIENT_SECRET,
            "scope":        SCOPE_ALL,
            "gatewayUrl": (
                "https://gw.sandbox.gopay.com"
                if settings.GOPAY_SANDBOX
                else "https://gate.gopay.cz"
            ),
        }
    )
