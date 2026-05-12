from django.contrib.auth.models import AbstractUser
from django.db import models

from shopforge.apps.core.models import TimeStampedModel
from shopforge.apps.users.managers import UserManager


class User(AbstractUser, TimeStampedModel):
    """
    Custom user model for ShopForge.

    Uses email as the primary login identifier instead of username.
    """

    class Role(models.TextChoices):
        """User roles in the platform."""

        CUSTOMER = "CUSTOMER", "Customer"
        STAFF = "STAFF", "Staff Member"
        VENDOR = "VENDOR", "Vendor"
        ADMIN = "ADMIN", "Administrator"

    # Override email to be required and unique
    email = models.EmailField(
        "email address",
        unique=True,
        error_messages={
            "unique": "A user with that email already exists.",
        },
    )

    # Additional fields
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )
    phone_number = models.CharField(max_length=20, blank=True)
    is_email_verified = models.BooleanField(default=False)

    objects = UserManager()

    # Use email as the login field (not username)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-date_joined"]

    def __str__(self):
        """Return human-readable representation."""
        return f"{self.get_full_name()} ({self.email})"

    @property
    def full_name(self):
        """Return the user's full name."""
        return self.get_full_name() or self.email
