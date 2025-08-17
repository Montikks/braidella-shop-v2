from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "name", "price", "qty", "line_total")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "total", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "id")
    inlines = [OrderItemInline]
    readonly_fields = ("subtotal", "shipping_price", "total", "created_at")
