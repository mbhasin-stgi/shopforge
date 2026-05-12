from django.apps import AppConfig


class AddressesConfig(AppConfig):
    """Saved shipping addresses for authenticated users."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "shopforge.apps.addresses"
    label = "addresses"
