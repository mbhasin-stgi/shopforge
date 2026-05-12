"""Wishlist models — saved products per user."""

from django.conf import settings
from django.db import models

from shopforge.apps.core.models import TimeStampedModel
from shopforge.apps.products.models import Product


class Wishlist(TimeStampedModel):
    """
    A user's wishlist (one per user, auto-created on first use).
    Products are stored via WishlistItem to capture the add timestamp.
    """

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist",
    )

    class Meta:
        verbose_name = "wishlist"

    def __str__(self):
        return f"Wishlist({self.owner.email})"


class WishlistItem(TimeStampedModel):
    """A product saved to a wishlist."""

    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlist_items")

    class Meta:
        unique_together = [("wishlist", "product")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.wishlist.owner.email} → {self.product.name}"
