from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse

from apps.checkout.forms import CheckoutForm, ShippingForm
from apps.orders.models import Order, OrderItem
from apps.shipping.models import ShippingMethod
from apps.cart.views import Cart

COD_FEE = Decimal("39.00")


def checkout(request):
    cart = Cart(request)
    if cart.count() == 0:
        messages.info(request, "Košík je prázdný.")
        return redirect("cart:detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            order = Order.objects.create(
                full_name=data["full_name"],
                email=data["email"],
                phone=data.get("phone", ""),
                street=data["street"],
                city=data["city"],
                zip_code=data["zip_code"],
                note=data.get("note", ""),
                subtotal=cart.subtotal(),
                shipping_price=Decimal("0.00"),
                total=cart.subtotal(),
                status="new",
            )
            for item in cart.items():
                OrderItem.objects.create(
                    order=order,
                    product=item["product"],
                    name=item["product"].name,
                    price=item["product"].price,
                    qty=item["qty"],
                    line_total=item["total"],
                )
            request.session["current_order_id"] = order.id
            messages.success(request, "Kontaktní údaje uloženy. Pokračuj výběrem dopravy a platby.")
            return redirect("checkout:shipping")
    else:
        form = CheckoutForm()

    return render(request, "checkout/checkout.html", {"form": form, "cart": cart})


def _get_or_bootstrap_order_from_session(request, cart: Cart):
    order = None
    order_id = request.session.get("current_order_id")
    if order_id:
        from apps.orders.models import Order as OrderModel
        try:
            order = OrderModel.objects.get(id=order_id, status="new")
        except OrderModel.DoesNotExist:
            order = None
    if not order:
        order = Order.objects.create(
            full_name="", email="", street="", city="", zip_code="",
            subtotal=cart.subtotal(), shipping_price=Decimal("0.00"),
            total=cart.subtotal(), status="new",
        )
        for item in cart.items():
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                name=item["product"].name,
                price=item["product"].price,
                qty=item["qty"],
                line_total=item["total"],
            )
        request.session["current_order_id"] = order.id
    return order


def shipping(request):
    cart = Cart(request)
    if cart.count() == 0:
        messages.info(request, "Košík je prázdný.")
        return redirect("cart:detail")

    order = _get_or_bootstrap_order_from_session(request, cart)

    if request.method == "POST":
        form = ShippingForm(request.POST)
        if form.is_valid():
            method: ShippingMethod = form.cleaned_data["method"]
            pay = form.cleaned_data["payment_method"]

            order.shipping_method = method.code
            order.shipping_price = method.price
            order.payment_method = pay

            if method.type == ShippingMethod.TYPE_PICKUP:
                order.pickup_provider = method.provider or ""
                order.pickup_point_id = form.cleaned_data.get("pickup_point_id", "")
                order.pickup_point_label = form.cleaned_data.get("pickup_point_label", "")
            else:
                order.pickup_provider = ""
                order.pickup_point_id = ""
                order.pickup_point_label = ""

            total = order.subtotal + order.shipping_price
            if pay == "cod":
                total += COD_FEE
            order.total = total
            order.save()

            messages.success(request, "Doprava a platba uložena. Pokračujeme na potvrzení.")
            return redirect("checkout:confirm")
    else:
        form = ShippingForm()

    methods = ShippingMethod.objects.filter(active=True).order_by("price")
    packeta_key = getattr(settings, "PACKETA_API_KEY", "")
    return render(
        request,
        "checkout/shipping.html",
        {
            "form": form,
            "methods": methods,
            "cart": cart,
            "cod_fee": COD_FEE,
            "order": order,
            "packeta_api_key": packeta_key,
        },
    )


def confirm_placeholder(request):
    return render(request, "checkout/confirm_placeholder.html", {})


# ======================
#  Fallback PPL výdejny
# ======================
def ppl_lookup(request):
    """
    Jednoduchý fallback bez externího API.
    Vrací JSON seznam výdejen dle prefixu PSČ.
    """
    zip_query = (request.GET.get("zip") or "").strip().replace(" ", "")
    # Mini "databáze" - můžeš kdykoli rozšířit nebo později napojit na reálné API.
    sample_points = [
        {"id": "PPL1001", "name": "PPL Parcelshop Praha Letná", "street": "Korunovační 10", "city": "Praha 7", "zip": "17000"},
        {"id": "PPL1002", "name": "PPL Parcelshop Praha Vršovice", "street": "Moskevská 20", "city": "Praha 10", "zip": "10100"},
        {"id": "PPL2001", "name": "PPL Parcelshop Brno Střed", "street": "Česká 5", "city": "Brno", "zip": "60200"},
        {"id": "PPL2002", "name": "PPL Parcelshop Brno Královo Pole", "street": "Purkyňova 1", "city": "Brno", "zip": "61200"},
        {"id": "PPL3001", "name": "PPL Parcelshop Ostrava Jih", "street": "Horní 32", "city": "Ostrava", "zip": "70030"},
        {"id": "PPL3002", "name": "PPL Parcelshop Ostrava Poruba", "street": "Hlavní třída 15", "city": "Ostrava", "zip": "70800"},
    ]
    items = []
    if zip_query:
        items = [p for p in sample_points if p["zip"].startswith(zip_query)]
    return JsonResponse({"ok": True, "items": items})
