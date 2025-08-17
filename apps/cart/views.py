from decimal import Decimal
from django.contrib import messages
from django.http import JsonResponse, HttpResponseNotAllowed
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from apps.catalog.models import Product

CART_SESSION_KEY = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, product_id: int, qty: int = 1, override: bool = False):
        product_id = str(product_id)
        item = self.cart.get(product_id)
        if item:
            item["qty"] = qty if override else item["qty"] + qty
        else:
            self.cart[product_id] = {"qty": max(1, qty)}
        self.save()

    def remove(self, product_id: int):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def items(self):
        ids = [int(pid) for pid in self.cart.keys()]
        products = {p.id: p for p in Product.objects.filter(id__in=ids)}
        for pid, data in self.cart.items():
            p = products.get(int(pid))
            if not p:
                continue
            qty = int(data["qty"])
            total = (p.price or Decimal("0")) * qty
            yield {"product": p, "qty": qty, "total": total}

    def subtotal(self):
        return sum(i["total"] for i in self.items())

    def count(self):
        return sum(int(i["qty"]) for i in self.cart.values())


# ---- Views (redirect flow) ----
@require_POST
def add(request, slug):
    product = get_object_or_404(Product, slug=slug, active=True)
    qty = max(1, int(request.POST.get("qty", 1)))
    if product.stock and qty > product.stock:
        messages.error(request, "Požadované množství není skladem.")
        return redirect(product.get_absolute_url())
    Cart(request).add(product.id, qty=qty)
    messages.success(request, f'Přidáno do košíku: "{product.name}".')
    return redirect("cart:detail")


@require_POST
def update(request, slug):
    product = get_object_or_404(Product, slug=slug, active=True)
    qty = max(1, int(request.POST.get("qty", 1)))
    if product.stock and qty > product.stock:
        messages.error(request, "Požadované množství není skladem.")
    else:
        Cart(request).add(product.id, qty=qty, override=True)
        messages.success(request, "Množství upraveno.")
    return redirect("cart:detail")


def remove(request, slug):
    product = get_object_or_404(Product, slug=slug)
    Cart(request).remove(product.id)
    messages.success(request, "Položka odstraněna.")
    return redirect("cart:detail")


def clear(request):
    Cart(request).clear()
    messages.success(request, "Košík vyprázdněn.")
    return redirect("cart:detail")


def detail(request):
    cart = Cart(request)
    return render(request, "cart/detail.html", {"cart": cart})


# ---- AJAX endpoint (no reload) ----
def mini(request):
    """Vrátí HTML obsahu mini-košíku (pro načtení/refresh draweru)."""
    cart = Cart(request)
    html = render_to_string("cart/_mini_body.html", {"cart": cart}, request=request)
    return JsonResponse({
        "ok": True,
        "html": html,
        "cart_count": cart.count(),
        "cart_subtotal": f"{cart.subtotal():.2f}",
    })

def add_ajax(request, slug):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    product = get_object_or_404(Product, slug=slug, active=True)
    try:
        qty = max(1, int(request.POST.get("qty", 1)))
    except (TypeError, ValueError):
        qty = 1

    if product.stock and qty > product.stock:
        return JsonResponse({"ok": False, "message": "Požadované množství není skladem."}, status=400)

    cart = Cart(request)
    cart.add(product.id, qty=qty)

    # hned po přidání vrátíme i HTML draweru
    html = render_to_string("cart/_mini_body.html", {"cart": cart}, request=request)
    return JsonResponse({
        "ok": True,
        "message": f'Přidáno do košíku: "{product.name}"',
        "cart_count": cart.count(),
        "cart_subtotal": f"{cart.subtotal():.2f}",
        "html": html,
    })