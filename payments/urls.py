from django.urls import path
from .views import start_payment, return_after_pay, notify

app_name = "payments"

urlpatterns = [
    path("start/", start_payment, name="start"),                 # ← jedno tlačítko volá POST sem
    path("return/<int:order_id>/", return_after_pay, name="return"),
    path("notify/", notify, name="notify"),
]
