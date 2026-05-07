"""
Order models — the heart of e-commerce.

An Order is a snapshot of what the customer bought, at what price, at what time.
Even if product prices change later, the order preserves the historical price.
"""
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from shopforge.apps.core.models import TimeStampedModel, UUIDModel
from shopforge.apps.products.models import Product


class Order(UUIDModel, TimeStampedModel):
    """
    Represents a customer's purchase.

    Key principle: Orders are IMMUTABLE records of what happened.
    Once placed, prices and quantities should not change
    (use refunds/adjustments instead).
    """

    class Status(models.TextChoices):
        """Order lifecycle states."""

        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        PROCESSING = "PROCESSING", "Processing"
        SHIPPED = "SHIPPED", "Shipped"
        DELIVERED = "DELIVERED", "Delivered"
        CANCELLED = "CANCELLED", "Cancelled"
        REFUNDED = "REFUNDED", "Refunded"

    class PaymentStatus(models.TextChoices):
        """Payment state for the order."""

        PENDING = "PENDING", "Payment Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Payment Failed"
        REFUNDED = "REFUNDED", "Refunded"
        PARTIALLY_REFUNDED = "PARTIAL_REFUND", "Partially Refunded"

    # Who placed the order
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # Never delete a user who has orders
        related_name="orders",
    )

    # Order state
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )

    # Pricing (calculated at order time, never recalculated)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    # Shipping address (denormalized — snapshot at order time)
    shipping_address_line1 = models.CharField(max_length=200)
    shipping_address_line2 = models.CharField(max_length=200, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default="US")

    # Tracking
    order_number = models.CharField(max_length=50, unique=True, editable=False)
    notes = models.TextField(blank=True, help_text="Internal notes about this order")
    tracking_number = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["customer", "status"]),
            models.Index(fields=["status", "payment_status"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        """Return order number and customer."""
        return f"Order {self.order_number} ({self.customer.email})"

    def save(self, *args, **kwargs):
        """Generate order number on first save."""
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def _generate_order_number(self):
        """Generate a unique, human-readable order number."""
        import time

        timestamp = int(time.time() * 1000) % 10000000
        return f"SF-{timestamp}"

    def calculate_totals(self):
        """Recalculate order totals from line items."""
        self.subtotal = sum(item.line_total for item in self.items.all())
        self.total = self.subtotal + self.tax_amount + self.shipping_cost - self.discount_amount
        self.save(update_fields=["subtotal", "total", "updated_at"])


class OrderItem(TimeStampedModel):
    """
    A single line item in an order.

    Key principle: We store price_at_purchase because product prices change.
    The order must always reflect what the customer actually paid.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,  # Can't delete products that have been ordered
        related_name="order_items",
    )

    # Snapshot at purchase time (immune to future price changes)
    product_name = models.CharField(max_length=300, help_text="Product name at time of purchase")
    product_sku = models.CharField(max_length=100, help_text="SKU at time of purchase")
    price_at_purchase = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Unit price when the order was placed",
    )
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        """Return item description."""
        return f"{self.quantity}x {self.product_name} @ ${self.price_at_purchase}"

    @property
    def line_total(self):
        """Calculate total for this line item."""
        return self.price_at_purchase * self.quantity

    def save(self, *args, **kwargs):
        """Auto-populate product snapshot fields on first save."""
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_sku:
            self.product_sku = self.product.sku
        super().save(*args, **kwargs)