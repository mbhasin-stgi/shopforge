from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Configuration for the Orders app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "shopforge.apps.orders"
    label = "orders"
    verbose_name = "Orders"

    def ready(self):
        """Wire up order signals on app startup."""
        import shopforge.apps.orders.signals  # noqa: F401
