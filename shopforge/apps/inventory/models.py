"""
Inventory management models.

Tracks stock levels and every movement (in/out) for audit purposes.
Think of it like a bank account: StockRecord is your balance,
StockMovement is your transaction history.
"""

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from shopforge.apps.core.models import TimeStampedModel
from shopforge.apps.products.models import Product


class StockRecord(TimeStampedModel):
    """
    Current stock level for a product.

    One product = one stock record (for simplicity; in real warehouse
    systems, you'd have one per warehouse location).
    """

    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="stock",
    )
    quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Current available quantity",
    )
    reserved_quantity = models.IntegerField(
        default=0,
        help_text="Quantity reserved by pending orders (not yet shipped)",
    )
    reorder_level = models.PositiveIntegerField(
        default=10,
        help_text="Alert when stock falls below this level",
    )
    reorder_quantity = models.PositiveIntegerField(
        default=50,
        help_text="How many to order when restocking",
    )

    class Meta:
        ordering = ["product__name"]

    def __str__(self):
        """Return stock info."""
        return f"{self.product.name}: {self.available_quantity} available"

    @property
    def available_quantity(self):
        """Stock available for new orders (total minus reserved)."""
        return self.quantity - self.reserved_quantity

    @property
    def needs_reorder(self):
        """Check if stock is below reorder threshold."""
        return self.available_quantity <= self.reorder_level


class StockMovement(TimeStampedModel):
    """
    Audit log of every stock change.

    Every increase or decrease is recorded with a reason.
    This is how you answer "where did our stock go?" in audits.
    """

    class MovementType(models.TextChoices):
        """Types of stock movements."""

        RECEIVED = "RECEIVED", "Stock Received"
        SOLD = "SOLD", "Sold (Order Fulfilled)"
        RETURNED = "RETURNED", "Customer Return"
        DAMAGED = "DAMAGED", "Damaged/Write-off"
        ADJUSTMENT = "ADJUSTMENT", "Manual Adjustment"
        RESERVED = "RESERVED", "Reserved for Order"
        UNRESERVED = "UNRESERVED", "Reservation Released"

    stock_record = models.ForeignKey(
        StockRecord,
        on_delete=models.CASCADE,
        related_name="movements",
    )
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    quantity_change = models.IntegerField(
        help_text="Positive = stock in, Negative = stock out",
    )
    reference = models.CharField(
        max_length=200,
        blank=True,
        help_text="Reference (e.g., order number, PO number)",
    )
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        """Return movement description."""
        direction = "+" if self.quantity_change > 0 else ""
        return (
            f"{self.get_movement_type_display()}: {direction}{self.quantity_change} ({self.stock_record.product.name})"
        )
