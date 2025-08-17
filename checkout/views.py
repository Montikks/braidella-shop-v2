from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from catalog.models import Product
from .forms import AddressForm
from orders.models import Order, OrderItem
from orders.email import send_order_confirmation
from uuid import uuid4
from django.shortcuts import render, redirect

CART_SESSION_KEY = "cart"
CHECKOUT_SESSION_KEY = "checkout_address"


def _cart_items_and_total(cart: dict):
    items, total = [], 0
    if not cart:
        return items, total

    p_ids = [int(k.split(":")[1]) for k in cart.keys() if isinstance(k, str) and k.startswith("p:")]
    products = {p.pk: p for p in Product.objects.filter(pk__in=p_ids).select_related("category")}

    for key, qty_raw in cart.items():
        if not (isinstance(key, str) and key.startswith("p:")):
            continue
        try:
            qty = max(0, int(qty_raw))
        except Exception:
            qty = 1
        if qty <= 0:
            continue

        pid = int(key.split(":")[1])
        p = products.get(pid)
        if not p:
            continue
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
    return items, total


def address(request):
    initial = request.session.get(CHECKOUT_SESSION_KEY, {})
    initial.setdefault("delivery_method", "address")
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            request.session[CHECKOUT_SESSION_KEY] = form.cleaned_data
            request.session.modified = True
            return redirect("checkout:review")
    else:
        form = AddressForm(initial=initial)
    return render(request, "checkout/address.html", {"form": form})


def review(request):
    cart = request.session.get(CART_SESSION_KEY, {})
    if not cart:
        messages.info(request, "Košík je prázdný.")
        return redirect("cart:detail")

    addr = request.session.get(CHECKOUT_SESSION_KEY)
    if not addr:
        messages.info(request, "Vyplňte prosím doručovací údaje.")
        return redirect("checkout:address")

    items, total = _cart_items_and_total(cart)
    if not items:
        messages.info(request, "Košík je prázdný.")
        return redirect("cart:detail")

    # --- Vytvoříme (nebo znovu použijeme) objednávku ve stavu 'new' ----
    order_id = request.session.get("order_id")
    if order_id:
        order = Order.objects.filter(pk=order_id, status="new").first()
    else:
        order = None

    if order is None:
        order = Order.objects.create(
            first_name=addr.get("first_name", ""),
            last_name=addr.get("last_name", ""),
            email=addr.get("email", ""),
            phone=addr.get("phone", ""),
            delivery_method=addr.get("delivery_method", "address"),
            street=addr.get("street", ""),
            city=addr.get("city", ""),
            zip_code=addr.get("zip_code", ""),
            balikovna_id=addr.get("balikovna_id", ""),
            balikovna_code=addr.get("balikovna_code", ""),
            ppl_id=addr.get("ppl_id", ""),
            ppl_code=addr.get("ppl_code", ""),
            total=total,
            status="new",
        )
        # uložíme ID do session, aby zůstalo stejné při opakovaném vstupu
        request.session["order_id"] = order.id
        request.session.modified = True

    return render(
        request,
        "checkout/review.html",
        {
            "items": items,
            "total": total,
            "addr": addr,
            "order": order,     # ← teď už existuje
        },
    )


def balikovna_picker(request):
    return render(request, "checkout/balikovna_picker.html")


# Widget pro výběr PPL výdejny. Po výběru pobočky widget pošle zprávu
# parent oknu (viz template). Zde pouze vykreslujeme stránku s widgetem.
def ppl_picker(request):
    return render(request, "checkout/ppl_picker.html")


def place_order(request):
    if request.method != "POST":
        return redirect("checkout:review")

    cart = request.session.get(CART_SESSION_KEY, {})
    if not cart:
        messages.info(request, "Košík je prázdný.")
        return redirect("cart:detail")

    addr = request.session.get(CHECKOUT_SESSION_KEY)
    if not addr:
        messages.info(request, "Vyplňte prosím doručovací údaje.")
        return redirect("checkout:address")

    items, total = _cart_items_and_total(cart)
    if not items:
        messages.info(request, "Košík je prázdný.")
        return redirect("cart:detail")

    # kontrola skladů
    for it in items:
        p = it["product"]
        stock = getattr(p, "stock", None)
        if stock is not None and it["qty"] > stock:
            messages.error(request, f"Na skladě je jen {stock} ks položky: {it['label']}.")
            return redirect("cart:detail")

    order = Order.objects.create(
        first_name=addr.get("first_name", ""),
        last_name=addr.get("last_name", ""),
        email=addr.get("email", ""),
        phone=addr.get("phone", ""),
        delivery_method=addr.get("delivery_method", "address"),
        street=addr.get("street", ""),
        city=addr.get("city", ""),
        zip_code=addr.get("zip_code", ""),
        balikovna_id=addr.get("balikovna_id", ""),
        balikovna_code=addr.get("balikovna_code", ""),
        ppl_id=addr.get("ppl_id", ""),
        ppl_code=addr.get("ppl_code", ""),
        total=total,
        status="new",
    )

    for it in items:
        p = it["product"]
        OrderItem.objects.create(
            order=order,
            product=p,
            name_snapshot=it["label"],
            price=it["price"],
            qty=it["qty"],
            subtotal=it["subtotal"],
        )
        if getattr(p, "stock", None) is not None:
            p.stock = max(0, p.stock - it["qty"])
            p.save(update_fields=["stock"])

    try:
        send_order_confirmation(order)
    except Exception as e:
        print("Order confirmation email failed:", e)

    try:
        del request.session[CART_SESSION_KEY]
    except KeyError:
        pass
    request.session.modified = True

    return redirect("checkout:success", order_id=order.id)


def success(request, order_id: int):
    from django.shortcuts import get_object_or_404
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "checkout/success.html", {"order": order})
