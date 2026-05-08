from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Configuration for the Orders app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "shopforge.apps.orders"
    label = "orders"
    verbose_name = "Orders"
