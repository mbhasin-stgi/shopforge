"""
Cart models — server-side, DB-backed shopping cart.

Design decisions:
- One cart per authenticated user (or anonymous session key).
- CartItem stores a price_snapshot so the cart total is accurate even if
  the product price changes while the user is browsing.
- Merging guest carts into user carts on login is handled in CartService.
"""

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from shopforge.apps.core.models import TimeStampedModel, UUIDModel
from shopforge.apps.products.models import Product


class Cart(UUIDModel, TimeStampedModel):
    """
    A shopping cart.

    Belongs to an authenticated user OR an anonymous session.
    On login, the session cart is merged into the user cart.
    """

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart",
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True,
        help_text="Session key for anonymous carts.",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(owner__isnull=False, session_key__isnull=True)
                    | models.Q(owner__isnull=True, session_key__isnull=False)
                ),
                name="cart_owner_xor_session",
            )
        ]

    def __str__(self):
        if self.owner:
            return f"Cart({self.owner.email})"
        return f"Cart(session={self.session_key})"

    @property
    def total(self) -> Decimal:
        """Sum of all line totals."""
        return sum((item.line_total for item in self.items.all()), Decimal("0.00"))

    @property
    def item_count(self) -> int:
        """Total number of units across all line items."""
        return sum(item.quantity for item in self.items.all())


class CartItem(TimeStampedModel):
    """
    A single line item in a cart.

    price_snapshot is captured at the moment the item is added so that
    the displayed cart total stays stable during browsing.
    """

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    price_snapshot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Product price at the time this item was added to the cart.",
    )

    class Meta:
        unique_together = [("cart", "product")]
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.quantity}× {self.product.name} @ ${self.price_snapshot}"

    @property
    def line_total(self) -> Decimal:
        """Price × quantity for this line."""
        return self.price_snapshot * self.quantity

    def save(self, *args, **kwargs):
        """Snapshot current product price on first add."""
        if not self.pk and not self.price_snapshot:
            self.price_snapshot = self.product.price
        super().save(*args, **kwargs)
