"""Admin configuration for product catalog models."""

from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, ProductImage, ProductVariant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for hierarchical product categories."""

    list_display = ["name", "parent", "display_order", "is_active", "product_count"]
    list_filter = ["is_active", "parent"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["display_order", "name"]

    @admin.display(description="Products")
    def product_count(self, obj):
        return obj.products.count()


class ProductVariantInline(admin.TabularInline):
    """Inline variant editor on the Product change page."""

    model = ProductVariant
    extra = 0
    fields = ["name", "sku", "price_override", "attributes", "is_active"]


class ProductImageInline(admin.TabularInline):
    """Inline image editor on the Product change page."""

    model = ProductImage
    extra = 1
    fields = ["image", "alt_text", "display_order", "is_primary", "thumbnail"]
    readonly_fields = ["thumbnail"]

    @admin.display(description="Preview")
    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="60" />', obj.image.url)
        return "—"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin for the core Product model.

    Shows soft-deleted products via list_filter so staff can audit them.
    Uses `all_objects` manager so nothing is hidden.
    """

    inlines = [ProductImageInline, ProductVariantInline]

    list_display = [
        "name",
        "sku",
        "category",
        "price",
        "compare_at_price",
        "status",
        "is_featured",
        "is_deleted",
        "created_at",
    ]
    list_filter = ["status", "is_featured", "is_deleted", "category"]
    search_fields = ["name", "sku", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["created_at", "updated_at", "is_on_sale", "discount_percentage", "profit_margin"]
    ordering = ["-created_at"]

    fieldsets = (
        ("Basic Information", {"fields": ("name", "slug", "sku", "category", "status", "is_featured")}),
        ("Description", {"fields": ("description", "short_description")}),
        (
            "Pricing",
            {
                "fields": (
                    "price",
                    "compare_at_price",
                    "cost_price",
                    "is_on_sale",
                    "discount_percentage",
                    "profit_margin",
                )
            },
        ),
        ("Physical", {"fields": ("weight",)}),
        ("SEO", {"fields": ("meta_title", "meta_description"), "classes": ("collapse",)}),
        ("Soft Delete", {"fields": ("is_deleted", "deleted_at"), "classes": ("collapse",)}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["mark_active", "mark_archived"]

    def get_queryset(self, request):
        """Use all_objects so soft-deleted products are visible in admin."""
        return self.model.all_objects.all()

    @admin.action(description="Mark selected products as Active")
    def mark_active(self, request, queryset):
        queryset.update(status=Product.Status.ACTIVE)

    @admin.action(description="Mark selected products as Archived")
    def mark_archived(self, request, queryset):
        queryset.update(status=Product.Status.ARCHIVED)
