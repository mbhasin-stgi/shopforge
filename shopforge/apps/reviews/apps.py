from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Product reviews and ratings."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "shopforge.apps.reviews"
    label = "reviews"
