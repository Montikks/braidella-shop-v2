from django.shortcuts import render, get_object_or_404
from .models import Category, Product

def categories(request):
    cats = Category.objects.order_by("ordering", "name")
    return render(request, "catalog/categories.html", {"categories": cats})

def category_detail(request, slug):
    cat = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=cat, active=True).order_by("name")
    return render(request, "catalog/category_detail.html", {"category": cat, "products": products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, active=True)
    return render(request, "catalog/product_detail.html", {"product": product})
