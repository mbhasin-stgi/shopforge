"""Coupon validation and application service."""

from decimal import Decimal

from django.db import transaction

from shopforge.apps.coupons.models import Coupon, CouponUsage


class CouponService:
    """Service for coupon operations."""

    @staticmethod
    def validate(code: str, customer, subtotal: Decimal) -> tuple[Coupon, Decimal]:
        """
        Validate a coupon code and return (coupon, discount_amount).

        Raises ValueError with a user-friendly message on any failure.
        Does NOT mutate any state (safe to call for preview/validation).
        """
        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            raise ValueError(f"Coupon code '{code}' does not exist.")

        if not coupon.is_valid:
            raise ValueError(f"Coupon '{code}' is expired or no longer valid.")

        if subtotal < coupon.min_order_amount:
            raise ValueError(f"Minimum order amount for coupon '{code}' is ${coupon.min_order_amount:.2f}.")

        discount = coupon.calculate_discount(subtotal)
        return coupon, discount

    @staticmethod
    @transaction.atomic
    def validate_and_apply(code: str, customer, order) -> Decimal:
        """
        Validate, apply a coupon to an order, and record the usage.

        Returns the discount amount applied.
        Raises ValueError if the coupon is invalid.
        """
        coupon, discount = CouponService.validate(code, customer, order.subtotal)

        CouponUsage.objects.create(
            coupon=coupon,
            order=order,
            user=customer,
            discount_applied=discount,
        )
        Coupon.objects.filter(pk=coupon.pk).update(uses_count=coupon.uses_count + 1)
        return discount
