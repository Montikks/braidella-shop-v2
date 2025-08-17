from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("pages.urls")),
    path("", include(("catalog.urls", "catalog"), namespace="catalog")),
    path("cart/", include(("cart.urls", "cart"), namespace="cart")),
    path("checkout/", include(("checkout.urls", "checkout"), namespace="checkout")),
    path("pay/", include(("payments.urls", "payments"), namespace="payments")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
