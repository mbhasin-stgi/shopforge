from django.apps import AppConfig


class CouponsConfig(AppConfig):
    """Discount coupons for orders."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "shopforge.apps.coupons"
    label = "coupons"
