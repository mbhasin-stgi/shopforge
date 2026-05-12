from django.contrib import admin

from shopforge.apps.cart.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Inline cart items within the Cart admin."""

    model = CartItem
    extra = 0
    readonly_fields = ("line_total", "created_at", "updated_at")
    fields = ("product", "quantity", "price_snapshot", "line_total")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for Cart — read-only overview for debugging."""

    list_display = ("__str__", "item_count", "total", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("owner__email", "session_key")
    inlines = [CartItemInline]
    readonly_fields = ("id", "total", "item_count", "created_at", "updated_at")
