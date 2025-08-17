from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.detail, name="detail"),
    path("add/<slug:slug>/", views.add, name="add"),
    path("update/<slug:slug>/", views.update, name="update"),
    path("remove/<slug:slug>/", views.remove, name="remove"),
    path("clear/", views.clear, name="clear"),

    # AJAX (bez reloadu)
    path("add-ajax/<slug:slug>/", views.add_ajax, name="add_ajax"),
    path("mini/", views.mini, name="mini"),
]
