"""Coupon API serializers."""

from decimal import Decimal

from rest_framework import serializers


class CouponValidateSerializer(serializers.Serializer):
    """Input for coupon validation preview."""

    code = serializers.CharField(max_length=50)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.00"),
        help_text="Order subtotal to calculate the discount against.",
    )


class CouponValidateResponseSerializer(serializers.Serializer):
    """Response for a valid coupon."""

    code = serializers.CharField()
    discount_type = serializers.CharField()
    discount_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    description = serializers.CharField()
