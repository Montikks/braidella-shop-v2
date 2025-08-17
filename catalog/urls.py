from django.urls import path
from .views import categories, category_detail, product_detail

app_name = "catalog"

urlpatterns = [
    path("k/", categories, name="categories"),                 # /k/
    path("k/<slug:slug>/", category_detail, name="category"),  # /k/<slug>/
    path("p/<slug:slug>/", product_detail, name="product"),    # /p/<slug>/
]
