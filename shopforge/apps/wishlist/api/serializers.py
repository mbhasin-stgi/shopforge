"""Wishlist serializers."""

from rest_framework import serializers

from shopforge.apps.products.api.serializers import ProductListSerializer
from shopforge.apps.wishlist.models import WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    """Serializer for a wishlist item with full product detail."""

    product_detail = ProductListSerializer(source="product", read_only=True)

    class Meta:
        model = WishlistItem
        fields = ["id", "product", "product_detail", "created_at"]
        read_only_fields = ["id", "created_at"]


class WishlistAddSerializer(serializers.Serializer):
    """Input for adding a product to the wishlist."""

    product_id = serializers.UUIDField()

    def validate_product_id(self, value):
        from shopforge.apps.products.models import Product

        try:
            return Product.objects.active().get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available.")
