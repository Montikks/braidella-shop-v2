from django.db import models
from orders.models import Order

class Payment(models.Model):
    order       = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    gopay_id    = models.BigIntegerField()
    gateway_url = models.URLField()
    state       = models.CharField(max_length=20, default="created")  # created/paid/canceled
    created     = models.DateTimeField(auto_now_add=True)
    updated     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment {self.gopay_id} for order {self.order_id}"
