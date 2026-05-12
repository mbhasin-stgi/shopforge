"""Order serializers with nested line items."""

from rest_framework import serializers

from shopforge.apps.orders.models import Order, OrderItem
from shopforge.apps.products.models import Product


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order line items."""

    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "price_at_purchase",
            "quantity",
            "line_total",
        ]
        read_only_fields = ["product_name", "product_sku", "price_at_purchase"]


class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer for creating order items (input validation)."""

    product_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        """Ensure product exists and is active."""
        try:
            Product.objects.active().get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available.")
        return value


class OrderListSerializer(serializers.ModelSerializer):
    """Lightweight order serializer for list views."""

    item_count = serializers.IntegerField(source="items.count", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "payment_status",
            "total",
            "item_count",
            "created_at",
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    """Full order serializer with all line items."""

    items = OrderItemSerializer(many=True, read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "customer_email",
            "status",
            "payment_status",
            "subtotal",
            "tax_amount",
            "shipping_cost",
            "discount_amount",
            "total",
            "shipping_address_line1",
            "shipping_address_line2",
            "shipping_city",
            "shipping_state",
            "shipping_postal_code",
            "shipping_country",
            "tracking_number",
            "notes",
            "items",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "order_number",
            "customer_email",
            # Financial fields — never recalculated by clients
            "subtotal",
            "tax_amount",
            "shipping_cost",
            "discount_amount",
            "total",
            # Status fields — only mutated via dedicated actions (cancel, ship, etc.)
            "status",
            "payment_status",
            "created_at",
            "updated_at",
        ]


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a new order.

    This is a plain Serializer (not ModelSerializer) because order creation
    involves complex logic: stock checking, price locking, payment initiation.
    The view/service handles the orchestration.
    """

    items = OrderItemCreateSerializer(many=True)
    shipping_address_line1 = serializers.CharField(max_length=200)
    shipping_address_line2 = serializers.CharField(max_length=200, required=False, default="")
    shipping_city = serializers.CharField(max_length=100)
    shipping_state = serializers.CharField(max_length=100)
    shipping_postal_code = serializers.CharField(max_length=20)
    shipping_country = serializers.CharField(max_length=100, default="US")

    def validate_items(self, value):
        """Ensure at least one item in the order."""
        if not value:
            raise serializers.ValidationError("Order must contain at least one item.")
        return value
