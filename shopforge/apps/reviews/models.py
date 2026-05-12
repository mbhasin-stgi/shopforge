"""Product review and rating models."""

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from shopforge.apps.core.models import TimeStampedModel
from shopforge.apps.products.models import Product


class Review(TimeStampedModel):
    """
    A customer review on a product.

    Each user can leave at most one review per product (unique_together).
    is_verified_purchase is set to True when the author has an order
    containing this product in DELIVERED status.
    """

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 (worst) to 5 (best).",
    )
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    is_verified_purchase = models.BooleanField(
        default=False,
        help_text="True when the author has a delivered order containing this product.",
    )
    is_approved = models.BooleanField(
        default=True,
        help_text="Admins can hide inappropriate reviews.",
    )

    class Meta:
        unique_together = [("product", "author")]
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "is_approved"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return f"{self.author.email} — {self.product.name} ({self.rating}★)"
