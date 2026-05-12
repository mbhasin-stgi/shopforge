"""Cart API serializers."""

from rest_framework import serializers

from shopforge.apps.cart.models import Cart, CartItem
from shopforge.apps.products.api.serializers import ProductListSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for a single cart line item."""

    product_detail = ProductListSerializer(source="product", read_only=True)
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_detail",
            "quantity",
            "price_snapshot",
            "line_total",
        ]
        read_only_fields = ["price_snapshot"]


class CartItemUpdateSerializer(serializers.Serializer):
    """Input for updating a cart item's quantity."""

    quantity = serializers.IntegerField(min_value=0)


class CartItemAddSerializer(serializers.Serializer):
    """Input for adding an item to the cart."""

    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_product_id(self, value):
        """Ensure product exists and is active."""
        from shopforge.apps.products.models import Product

        try:
            return Product.objects.active().get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available.")


class CartSerializer(serializers.ModelSerializer):
    """Full cart serializer."""

    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    item_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "items", "total", "item_count", "updated_at"]


class CartCheckoutSerializer(serializers.Serializer):
    """Input for converting a cart into an order."""

    shipping_address_line1 = serializers.CharField(max_length=200)
    shipping_address_line2 = serializers.CharField(max_length=200, required=False, default="")
    shipping_city = serializers.CharField(max_length=100)
    shipping_state = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=20)
    shipping_country = serializers.CharField(max_length=100, default="US")
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
