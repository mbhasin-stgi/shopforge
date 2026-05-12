from django.apps import AppConfig


class WishlistConfig(AppConfig):
    """User wishlists / saved products."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "shopforge.apps.wishlist"
    label = "wishlist"
