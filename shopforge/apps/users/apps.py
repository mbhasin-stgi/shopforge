from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration for the Users app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "shopforge.apps.users"
    label = "users"
    verbose_name = "Users"

    def ready(self):
        """Wire up user signals on app startup."""
        import shopforge.apps.users.signals  # noqa: F401
