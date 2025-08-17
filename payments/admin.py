from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "gopay_id", "state", "created")
    search_fields = ("gopay_id", "order__id")
    list_filter = ("state",)
