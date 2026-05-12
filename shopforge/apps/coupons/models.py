"""Coupon and coupon usage models."""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from shopforge.apps.core.models import TimeStampedModel


class Coupon(TimeStampedModel):
    """
    A discount coupon.

    Supports two discount types:
    - PERCENT: discount_value% off order subtotal (capped at 100%)
    - FIXED: fixed amount off order subtotal

    Use max_uses=None (null) for unlimited-use coupons.
    """

    class DiscountType(models.TextChoices):
        PERCENT = "PERCENT", "Percentage Discount"
        FIXED = "FIXED", "Fixed Amount Discount"

    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.CharField(max_length=300, blank=True)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices, default=DiscountType.PERCENT)
    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Percentage (0–100) or fixed amount, depending on discount_type.",
    )
    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Minimum order subtotal for the coupon to apply.",
    )
    max_uses = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of uses (null = unlimited).",
    )
    uses_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} ({self.discount_type} {self.discount_value})"

    @property
    def is_valid(self) -> bool:
        """Check if coupon is currently valid (active, within dates, usage not exhausted)."""
        now = timezone.now()
        if not self.is_active:
            return False
        if not (self.valid_from <= now <= self.valid_until):
            return False
        if self.max_uses is not None and self.uses_count >= self.max_uses:
            return False
        return True

    def calculate_discount(self, subtotal: Decimal) -> Decimal:
        """Return the discount amount for the given subtotal."""
        if self.discount_type == self.DiscountType.PERCENT:
            return (subtotal * self.discount_value / Decimal("100")).quantize(Decimal("0.01"))
        return min(self.discount_value, subtotal)


class CouponUsage(TimeStampedModel):
    """
    Audit record of a coupon being applied to an order.

    Allows per-user usage limits to be checked when needed.
    """

    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usages")
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="coupon_usages",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="coupon_usages",
    )
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = [("coupon", "order")]

    def __str__(self):
        return f"{self.coupon.code} on order {self.order.order_number}"
