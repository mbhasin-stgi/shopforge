from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """Configuration for the Products app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "shopforge.apps.products"
    label = "products"
    verbose_name = "Products"