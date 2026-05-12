from django.apps import AppConfig


class CartConfig(AppConfig):
    """Cart application — server-side, DB-backed shopping cart."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "shopforge.apps.cart"
    label = "cart"

    def ready(self):
        """Wire up signals on app startup."""
        import shopforge.apps.cart.signals  # noqa: F401
