from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from catalog.models import Product
from orders.models import Order, OrderItem
from orders.email import send_order_confirmation
from .gateway import gopay_client
from .models import Payment

CART_SESSION_KEY = "cart"
CHECKOUT_SESSION_KEY = "checkout_address"


def _cart_items_and_total(cart: dict):
    """Lokální kopie – ať nejsme závislí na jiných modulech."""
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
        items.append(
            {
                "product": p,
                "qty": qty,
                "price": price,
                "subtotal": subtotal,
                "label": p.name,
            }
        )
        total += subtotal
    return items, total


def _ensure_order_and_items(request):
    """
    1) Z adresy v session vytvoří/aktualizuje Order (status='new').
    2) Pokud Order nemá položky, vytvoří OrderItem snapshoty podle košíku.
    """
    cart = request.session.get(CART_SESSION_KEY, {})
    if not cart:
        return None, ("Košík je prázdný.", "cart:detail")

    addr = request.session.get(CHECKOUT_SESSION_KEY)
    if not addr:
        return None, ("Vyplňte prosím doručovací údaje.", "checkout:address")

    items, total = _cart_items_and_total(cart)
    if not items:
        return None, ("Košík je prázdný.", "cart:detail")

    order_id = request.session.get("order_id")
    order = (
        Order.objects.filter(pk=order_id, status="new").first()
        if order_id
        else None
    )
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
            total=total,
            status="new",
        )
        request.session["order_id"] = order.id
        request.session.modified = True
    else:
        # udržet total aktuální (kdyby se košík změnil)
        order.total = total
        order.save(update_fields=["total"])

    if order.items.count() == 0:
        # založit snapshot položek
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
            # (volitelně) rezervace skladu – pokud má pole stock
            if getattr(p, "stock", None) is not None:
                p.stock = max(0, p.stock - it["qty"])
                p.save(update_fields=["stock"])

    return order, None


def start_payment(request):
    """
    Jedno tlačítko:
    - založí/aktualizuje objednávku + položky
    - vytvoří platbu u GoPay
    - redirect na bránu
    """
    if request.method != "POST":
        return redirect("checkout:review")

    order, fail = _ensure_order_and_items(request)
    if fail:
        msg, where = fail
        messages.info(request, msg)
        return redirect(where)

    gp = gopay_client()
    items = [
        {"name": it.name_snapshot, "amount": int(it.subtotal * Decimal("100")), "count": it.qty}
        for it in order.items.all()
    ]

    response = gp.create_payment(
        {
            "payer": {"allowed_payment_instruments": ["PAYMENT_CARD"]},
            "target": {"type": "ACCOUNT", "goid": settings.GOPAY_GOID},
            "amount": int(order.total * Decimal("100")),
            "currency": "CZK",
            "order_number": str(order.id),
            "order_description": f"Braidella objednávka #{order.id}",
            "items": items,
            "callback": {
                "return_url": request.build_absolute_uri(reverse("payments:return", args=[order.id])),
                "notification_url": request.build_absolute_uri(reverse("payments:notify")),
            },
        }
    )
    if getattr(settings, "PAYMENTS_FAKE", False):
        from .models import Payment
        Payment.objects.update_or_create(
            order=order,
            defaults={"gopay_id": 0, "gateway_url": "", "state": "paid"},
        )
        order.status = "paid"
        order.save(update_fields=["status"])
        for key in ("cart", "order_id"):
            request.session.pop(key, None)
        request.session.modified = True
        from django.contrib import messages
        messages.success(request, "Platba byla úspěšně simulována (DEV).")
        return redirect("payments:return", order_id=order.id)

    # Nové SDK má metodu has_succeed()
    if getattr(response, "has_succeed", None) and response.has_succeed():
        data = response.json
        Payment.objects.update_or_create(
            order=order,
            defaults={
                "gopay_id": data["id"],
                "gateway_url": data["gw_url"],
                "state": "created",
            },
        )
        return redirect(data["gw_url"])

    # Debug pro případ chyby (v dev konsoli)
    try:
        print("GoPay create_payment failed:", response.json)
    except Exception:
        pass
    messages.error(request, "Platbu se nepodařilo založit. Zkuste to prosím znovu.")
    return redirect("checkout:review")


@csrf_exempt
def notify(request):
    """Server-to-server notifikace od GoPay."""
    import json

    body = json.loads(request.body or "{}")
    payment_id = body.get("id")
    if not payment_id:
        return HttpResponse(status=400)

    gp = gopay_client()
    status = gp.get_status(payment_id).json
    pay = Payment.objects.filter(gopay_id=payment_id).select_related("order").first()
    if not pay:
        return HttpResponse(status=404)

    if status.get("state") == "PAID" and pay.order.status == "new":
        pay.state = "paid"
        pay.save(update_fields=["state"])
        pay.order.status = "paid"
        pay.order.save(update_fields=["status"])
        # e-mail zákazníkovi
        try:
            send_order_confirmation(pay.order)
        except Exception as e:
            print("Order confirmation email failed:", e)

    return HttpResponse("OK")


def return_after_pay(request, order_id: int):
    """
    Po návratu z brány:
    - pokud notify nepřišel (localhost), zkusíme dotázat GoPay na stav
    - pokud je PAID, označíme objednávku + platbu jako 'paid' a vyčistíme košík
    """
    order = get_object_or_404(Order, pk=order_id)

    # když není zaplaceno a máme payment, zkus zjistit stav z API
    if order.status != "paid" and hasattr(order, "payment"):
        gp = gopay_client()
        try:
            st = gp.get_status(order.payment.gopay_id).json
            if st.get("state") == "PAID":
                order.payment.state = "paid"
                order.payment.save(update_fields=["state"])
                order.status = "paid"
                order.save(update_fields=["status"])
        except Exception as e:
            print("GoPay get_status error:", e)

    # pokud už je paid, vyčisti košík a session
    if order.status == "paid":
        for key in (CART_SESSION_KEY, "order_id"):
            try:
                del request.session[key]
            except KeyError:
                pass
        request.session.modified = True

    return render(request, "payments/return.html", {"order": order})

