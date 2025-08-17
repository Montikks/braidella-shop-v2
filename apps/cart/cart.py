from decimal import Decimal
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

    # iterace s napojenými produkty a cenami
    def items(self):
        ids = [int(pid) for pid in self.cart.keys()]
        products = {p.id: p for p in Product.objects.filter(id__in=ids)}
        for pid, data in self.cart.items():
            p = products.get(int(pid))
            if not p:
                continue
            qty = data["qty"]
            total = (p.price or Decimal("0")) * qty
            yield {"product": p, "qty": qty, "total": total}

    def subtotal(self):
        return sum(i["total"] for i in self.items())

    def count(self):
        return sum(i["qty"] for i in self.cart.values())
