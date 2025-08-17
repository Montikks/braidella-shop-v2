from django.contrib import admin
from .models import ShippingMethod

@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "type", "price", "cod_supported", "active", "provider", "cost_to_merchant")
    list_filter = ("type", "active", "cod_supported", "provider")
    search_fields = ("name", "code")
