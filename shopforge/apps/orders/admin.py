"""Admin configuration for order models."""

from django.contrib import admin
from django.utils.html import format_html

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline order items on the Order change page."""

    model = OrderItem
    extra = 0
    fields = ["product", "product_name", "product_sku", "price_at_purchase", "quantity", "display_line_total"]
    readonly_fields = ["product_name", "product_sku", "display_line_total"]

    @admin.display(description="Line Total")
    def display_line_total(self, obj):
        """Safe wrapper — returns em-dash for unsaved/empty rows."""
        total = obj.line_total
        return f"${total}" if total is not None else "—"

    def has_add_permission(self, request, obj=None):
        """Prevent adding new items to existing orders via admin."""
        return obj is None

    def has_delete_permission(self, request, obj=None):
        """Prevent removing items from existing orders via admin."""
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin for Order model.

    Key design decisions:
    - Most fields are read-only — orders are immutable records.
    - Staff can update status/tracking but not pricing.
    """

    inlines = [OrderItemInline]

    list_display = [
        "order_number",
        "customer_email",
        "status",
        "payment_status",
        "total",
        "item_count",
        "created_at",
    ]
    list_filter = ["status", "payment_status", "created_at"]
    search_fields = ["order_number", "customer__email", "customer__first_name", "customer__last_name"]
    readonly_fields = [
        "order_number",
        "subtotal",
        "tax_amount",
        "shipping_cost",
        "discount_amount",
        "total",
        "created_at",
        "updated_at",
    ]
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Order Info", {"fields": ("order_number", "customer", "status", "payment_status")}),
        (
            "Shipping Address",
            {
                "fields": (
                    "shipping_address_line1",
                    "shipping_address_line2",
                    "shipping_city",
                    "shipping_state",
                    "shipping_postal_code",
                    "shipping_country",
                ),
            },
        ),
        (
            "Totals",
            {
                "fields": ("subtotal", "tax_amount", "shipping_cost", "discount_amount", "total"),
            },
        ),
        ("Tracking & Notes", {"fields": ("tracking_number", "notes")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["mark_confirmed", "mark_shipped", "mark_delivered"]

    @admin.display(description="Customer")
    def customer_email(self, obj):
        return obj.customer.email

    @admin.display(description="Items")
    def item_count(self, obj):
        return obj.items.count()

    @admin.display(description="Total", ordering="total")
    def colored_total(self, obj):
        return format_html("<strong>${}</strong>", obj.total)

    @admin.action(description="Mark selected orders as Confirmed")
    def mark_confirmed(self, request, queryset):
        queryset.filter(status=Order.Status.PENDING).update(status=Order.Status.CONFIRMED)

    @admin.action(description="Mark selected orders as Shipped")
    def mark_shipped(self, request, queryset):
        queryset.filter(status=Order.Status.PROCESSING).update(status=Order.Status.SHIPPED)

    @admin.action(description="Mark selected orders as Delivered")
    def mark_delivered(self, request, queryset):
        queryset.filter(status=Order.Status.SHIPPED).update(status=Order.Status.DELIVERED)
