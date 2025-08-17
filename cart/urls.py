from django.urls import path
from .views import detail, add, update, remove

app_name = "cart"

urlpatterns = [
    path("", detail, name="detail"),
    path("add/", add, name="add"),
    path("update/", update, name="update"),
    path("remove/<str:key>/", remove, name="remove"),  # key je např. "p:34" nebo "v:12"
]
