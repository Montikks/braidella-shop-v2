from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product_list"),
    path("k/<slug:category_slug>/", views.ProductListView.as_view(), name="product_list_by_category"),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
]
