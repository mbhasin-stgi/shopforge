"""
Product serializers.

Serializers do TWO jobs:
1. Validation — ensure incoming data is valid before it hits the database
2. Transformation — control what data goes out (hide internal fields, add computed fields)
"""

from rest_framework import serializers

from shopforge.apps.products.models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product categories."""

    product_count = serializers.IntegerField(read_only=True, default=0)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "is_active",
            "display_order",
            "product_count",
            "children",
        ]
        read_only_fields = ["slug"]

    def get_children(self, obj):
        """Return child categories (one level deep to avoid infinite recursion)."""
        children = obj.children.filter(is_active=True)
        return CategoryListSerializer(children, many=True).data


class CategoryListSerializer(serializers.ModelSerializer):
    """Lightweight category serializer for list views and nested usage."""

    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""

    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "display_order", "is_primary"]


class ProductListSerializer(serializers.ModelSerializer):
    """
    Lightweight product serializer for list views.

    Why a separate list serializer?
    - List views return 25+ items. Each extra field × 25 = slower response.
    - We don't need full description in a product grid.
    - Fewer database joins needed (better performance).
    """

    category_name = serializers.CharField(source="category.name", read_only=True)
    primary_image = serializers.SerializerMethodField()
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "short_description",
            "price",
            "compare_at_price",
            "category_name",
            "status",
            "is_featured",
            "is_on_sale",
            "discount_percentage",
            "primary_image",
            "created_at",
        ]

    def get_primary_image(self, obj):
        """Return URL of the primary product image."""
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            return self.context["request"].build_absolute_uri(primary.image.url)
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Full product serializer for detail views.

    Includes everything: all images, computed properties, related data.
    """

    category = CategoryListSerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
    )
    images = ProductImageSerializer(many=True, read_only=True)
    is_on_sale = serializers.BooleanField(read_only=True)
    discount_percentage = serializers.IntegerField(read_only=True)
    profit_margin = serializers.FloatField(read_only=True)
    in_stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "short_description",
            "category",
            "category_id",
            "price",
            "compare_at_price",
            "cost_price",
            "sku",
            "status",
            "is_featured",
            "weight",
            "meta_title",
            "meta_description",
            "images",
            "is_on_sale",
            "discount_percentage",
            "profit_margin",
            "in_stock",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def get_in_stock(self, obj):
        """Check if product has available stock."""
        if hasattr(obj, "stock"):
            return obj.stock.available_quantity > 0
        return False
