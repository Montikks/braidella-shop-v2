from decimal import Decimal
from django.db import models

class ShippingMethod(models.Model):
    TYPE_PICKUP = "pickup_point"
    TYPE_HOME = "home_delivery"
    TYPE_CHOICES = [
        (TYPE_PICKUP, "Výdejní místo"),
        (TYPE_HOME, "Doručení na adresu"),
    ]

    PROVIDER_CHOICES = [
        ("balikovna", "Balíkovna"),
        ("zasilkovna", "Zásilkovna"),
        ("ppl", "PPL"),
        (None, "—"),
    ]

    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    cod_supported = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, blank=True, null=True)
    cost_to_merchant = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.price} Kč)"
