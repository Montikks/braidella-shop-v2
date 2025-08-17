from django.urls import path
from .views import address, review, balikovna_picker, ppl_picker, place_order, success

app_name = "checkout"

urlpatterns = [
    path("", address, name="address"),
    path("review/", review, name="review"),
    path("balikovna/picker/", balikovna_picker, name="balikovna_picker"),
    path("ppl/picker/", ppl_picker, name="ppl_picker"),
    path("place/", place_order, name="place"),
    path("success/<int:order_id>/", success, name="success"),
]
