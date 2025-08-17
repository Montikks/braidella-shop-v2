from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Order, OrderItem
from .email import send_tracking_email

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "name_snapshot", "price", "qty", "subtotal")
    fields = ("product", "name_snapshot", "price", "qty", "subtotal")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "last_name", "email", "total", "status", "carrier", "tracking_code", "shipped_at", "created")
    list_filter = ("status", "carrier", "created")
    search_fields = ("id", "last_name", "email", "phone", "balikovna_code", "ppl_code", "zip_code", "tracking_code")
    inlines = [OrderItemInline]
    readonly_fields = ("created", "updated", "tracking_link")

    fieldsets = (
        ("Zákazník", {"fields": ("first_name", "last_name", "email", "phone")}),
        ("Doručení", {"fields": ("delivery_method", "street", "city", "zip_code", "balikovna_id", "balikovna_code", "ppl_id", "ppl_code")}),
        ("Stav a platba", {"fields": ("status", "total")}),
        ("Sledování zásilky", {"fields": ("carrier", "tracking_code", "shipped_at", "tracking_link")}),
        ("Systém", {"fields": ("created", "updated")}),
    )

    actions = ["mark_as_shipped_and_email", "send_tracking_only"]

    def tracking_link(self, obj):
        url = obj.tracking_url()
        if url:
            return format_html('<a href="{}" target="_blank">Otevřít sledování</a>', url)
        return "-"
    tracking_link.short_description = "Sledování"

    def mark_as_shipped_and_email(self, request, queryset):
        count = 0
        for order in queryset:
            if not order.tracking_code:
                continue
            if not order.shipped_at:
                order.shipped_at = timezone.now()
            order.status = "shipped"
            order.save(update_fields=["status", "shipped_at"])
            try:
                send_tracking_email(order)
            except Exception:
                pass
            count += 1
        self.message_user(request, f"Označeno jako odeslané a odeslán e-mail: {count} objednávek.")
    mark_as_shipped_and_email.short_description = "Označit jako odeslané + poslat tracking e-mail"

    def send_tracking_only(self, request, queryset):
        count = 0
        for order in queryset:
            if not order.tracking_code:
                continue
            try:
                send_tracking_email(order)
            except Exception:
                pass
            count += 1
        self.message_user(request, f"Odeslán tracking e-mail: {count} objednávek.")
    send_tracking_only.short_description = "Poslat tracking e-mail (bez změny stavu)"
