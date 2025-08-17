from decimal import Decimal
from django.db import models
from django.urls import reverse
from apps.catalog.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Nová"),
        ("paid", "Zaplaceno"),
        ("shipped", "Odesláno"),
        ("cancelled", "Zrušeno"),
    ]

    # zákazník
    full_name = models.CharField("Jméno a příjmení", max_length=160)
    email = models.EmailField("E‑mail")
    phone = models.CharField("Telefon", max_length=40, blank=True)

    # adresa (CZ jednoduše)
    street = models.CharField("Ulice a č.p.", max_length=160)
    city = models.CharField("Město", max_length=120)
    zip_code = models.CharField("PSČ", max_length=20)

    note = models.TextField("Poznámka", blank=True)

    # totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    # stav/platba (zatím jednoduše)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    payment_method = models.CharField(max_length=20, blank=True)

    # doprava (vyplníme v kroku 2)
    shipping_method = models.CharField(max_length=50, blank=True)
    pickup_provider = models.CharField(max_length=50, blank=True)
    pickup_point_id = models.CharField(max_length=100, blank=True)
    pickup_point_label = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Objednávka #{self.id} – {self.full_name}"

    def get_absolute_url(self):
        return reverse("orders:detail", args=[self.pk])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField(default=1)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} × {self.qty}"
