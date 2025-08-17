from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Product, Category

class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        qs = Product.objects.filter(active=True).select_related("category")
        cat = self.kwargs.get("category_slug")
        if cat:
            qs = qs.filter(category__slug=cat)
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(name__icontains=q)
        order = self.request.GET.get("order")
        if order == "price":
            qs = qs.order_by("price")
        elif order == "-price":
            qs = qs.order_by("-price")
        else:
            qs = qs.order_by("name")
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Category.objects.all()
        ctx["current_category"] = None
        if "category_slug" in self.kwargs:
            ctx["current_category"] = get_object_or_404(Category, slug=self.kwargs["category_slug"])
        ctx["q"] = self.request.GET.get("q", "")
        ctx["order"] = self.request.GET.get("order", "")
        return ctx

class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
