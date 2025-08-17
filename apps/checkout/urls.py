from django.urls import path
from . import views

app_name = "checkout"

urlpatterns = [
    path("", views.checkout, name="start"),
    path("shipping/", views.shipping, name="shipping"),
    path("confirm/", views.confirm_placeholder, name="confirm"),
    # Fallback vyhledávání PPL výdejen podle PSČ (mock data)
    path("ppl-lookup/", views.ppl_lookup, name="ppl_lookup"),
]
