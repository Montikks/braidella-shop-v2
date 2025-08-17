from django.db import models
from catalog.models import Product


class Order(models.Model):
    # zákazník
    first_name = models.CharField(max_length=60)
    last_name = models.CharField(max_length=60)
    email = models.EmailField(max_length=120)
    phone = models.CharField(max_length=20)

    # doručení
    # způsob doručení. Přidáme možnost PPL výdejního místa.
    DELIVERY_CHOICES = [
        ("address", "Doručení na adresu"),
        ("balikovna", "Balíkovna"),
        ("ppl", "PPL Parcelshop"),
    ]
    delivery_method = models.CharField(max_length=20, choices=DELIVERY_CHOICES)

    street = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=80, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)

    # Balíkovna
    balikovna_id = models.CharField(max_length=255, blank=True)
    balikovna_code = models.CharField(max_length=32, blank=True)

    # PPL parcelshop – obdobné jako Balíkovna: ukládáme čitelné ID (popisek) a kód
    ppl_id = models.CharField(max_length=255, blank=True)
    ppl_code = models.CharField(max_length=32, blank=True)

    # ceny a stav
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    STATUS_CHOICES = [
        ("new", "Nová"),
        ("paid", "Zaplacená"),
        ("canceled", "Zrušená"),
        ("shipped", "Odeslaná"),
        ("done", "Dokončená"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")

    # dopravce / tracking (ponecháme)
    CARRIER_CHOICES = [
        ("czp_balikovna", "Česká pošta – Balíkovna"),
        ("czp", "Česká pošta (ostatní)"),
        ("ppl", "PPL"),
        ("other", "Jiný dopravce"),
    ]
    carrier = models.CharField(max_length=32, choices=CARRIER_CHOICES, default="czp_balikovna")
    tracking_code = models.CharField(max_length=64, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Objednávka #{self.pk} – {self.last_name}"

    def tracking_url(self):
        code = (self.tracking_code or "").strip()
        if not code:
            return ""
        if self.carrier == "czp_balikovna":
            return f"https://www.balikovna.cz/cs/sledovat-balik/-/balik/{code}"
        if self.carrier == "czp":
            return f"https://www.postaonline.cz/cz/trackandtrace?parcelNumbers={code}"
        if self.carrier == "ppl":
            # PPL tracking – oficiální stránka umožňuje zadat shipment number. URL se může měnit,
            # ale použijeme obecný tvar; uživatel může kód zkopírovat.
            return f"https://www.ppl.cz/sledovani-zasilky?shipID={code}"
        return ""


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")

    name_snapshot = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.name_snapshot} × {self.qty}"
