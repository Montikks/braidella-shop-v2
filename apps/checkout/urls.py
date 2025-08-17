from django.urls import path

from . import views


app_name = "checkout"


urlpatterns = [
    # Start checkout – zadání kontaktních údajů
    path("", views.checkout, name="start"),
    # Výběr dopravy a platby
    path("shipping/", views.shipping, name="shipping"),
    # Potvrzení objednávky (placeholder)
    path("confirm/", views.confirm_placeholder, name="confirm"),
    # Stránka s mapou PPL pro výběr výdejny
    path("ppl-picker/", views.ppl_picker, name="ppl_picker"),
    # Fallback vyhledávání PPL výdejen podle PSČ (mock data)
    path("ppl-lookup/", views.ppl_lookup, name="ppl_lookup"),
]