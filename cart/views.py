from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from catalog.models import Product

CART_SESSION_KEY = "cart"  # dict: {"p:<id>": qty}

def _get_cart(session):
    return session.setdefault(CART_SESSION_KEY, {})

def _key_for(product_id):
    return f"p:{int(product_id)}"

def add(request):
    if request.method != "POST":
        return redirect("cart:detail")

    product_id = request.POST.get("product_id")
    qty_raw = request.POST.get("qty", "1")

    try:
        qty = max(1, int(qty_raw))
    except ValueError:
        qty = 1

    if not product_id:
        messages.error(request, "Nebyla uvedena položka.")
        return redirect("cart:detail")

    p = get_object_or_404(Product, pk=product_id, active=True)
    if p.stock is not None and qty > p.stock:
        qty = p.stock
        if qty <= 0:
            messages.error(request, "Položka není skladem.")
            return redirect("cart:detail")

    cart = _get_cart(request.session)
    key = _key_for(product_id)
    cart[key] = cart.get(key, 0) + qty
    request.session.modified = True
    messages.success(request, f"Přidáno do košíku: {p.name} (×{qty})")
    return redirect("cart:detail")

def update(request):
    if request.method != "POST":
        return redirect("cart:detail")

    key = request.POST.get("key")
    qty_raw = request.POST.get("qty", "1")

    try:
        qty = max(0, int(qty_raw))
    except ValueError:
        qty = 1

    cart = _get_cart(request.session)

    if not key or not key.startswith("p:"):
        return redirect("cart:detail")

    pid = int(key.split(":")[1])
    p = get_object_or_404(Product, pk=pid, active=True)

    if p.stock is not None:
        qty = min(qty, max(0, p.stock))

    if qty <= 0:
        cart.pop(key, None)
        messages.info(request, "Položka odebrána z košíku.")
    else:
        cart[key] = qty
        messages.success(request, f"Množství upraveno na ×{qty}.")
    request.session.modified = True
    return redirect("cart:detail")

def remove(request, key):
    if request.method != "POST":
        return redirect("cart:detail")
    cart = request.session.get(CART_SESSION_KEY, {})
    if key in cart:
        cart.pop(key)
        request.session.modified = True
        messages.info(request, "Položka odebrána z košíku.")
    return redirect("cart:detail")

def detail(request):
    cart = request.session.get(CART_SESSION_KEY, {})
    items = []
    total = 0

    if cart:
        p_ids = [int(k.split(":")[1]) for k in cart.keys() if k.startswith("p:")]
        products = {p.pk: p for p in Product.objects.filter(pk__in=p_ids).select_related("category")}
        for key, qty_val in cart.items():
            if not key.startswith("p:"):
                continue
            pid = int(key.split(":")[1])
            p = products.get(pid)
            if not p:
                continue
            try:
                qty = int(qty_val)
            except ValueError:
                qty = 1
            price = p.price
            subtotal = price * qty
            items.append({
                "key": key,
                "product": p,
                "qty": qty,
                "price": price,
                "subtotal": subtotal,
                "label": p.name,
            })
            total += subtotal

    return render(request, "cart/detail.html", {"items": items, "total": total})
