"""Saved shipping address models."""

from django.conf import settings
from django.db import models

from shopforge.apps.core.models import TimeStampedModel, UUIDModel


class UserAddress(UUIDModel, TimeStampedModel):
    """
    A saved shipping address belonging to a user.

    Users can have multiple addresses; one is marked is_default.
    Addresses are denormalised onto orders at checkout time (snapshot).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )
    label = models.CharField(
        max_length=100,
        blank=True,
        help_text="Friendly name, e.g. 'Home', 'Office'.",
    )
    full_name = models.CharField(max_length=200)
    line1 = models.CharField("Address line 1", max_length=200)
    line2 = models.CharField("Address line 2", max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="US")
    phone = models.CharField(max_length=30, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ["-is_default", "-created_at"]
        verbose_name = "address"
        verbose_name_plural = "addresses"

    def __str__(self):
        return f"{self.label or 'Address'} — {self.line1}, {self.city}"

    def save(self, *args, **kwargs):
        """Ensure only one default address per user."""
        if self.is_default:
            UserAddress.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
