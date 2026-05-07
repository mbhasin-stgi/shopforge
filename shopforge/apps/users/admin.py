"""Admin configuration for User model."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin view for the custom User model."""

    list_display = ["email", "first_name", "last_name", "role", "is_active", "date_joined"]
    list_filter = ["role", "is_active", "is_staff", "is_email_verified"]
    search_fields = ["email", "first_name", "last_name"]
    ordering = ["-date_joined"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone_number")}),
        ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "is_email_verified")}),
        ("Groups", {"fields": ("groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2", "role")}),
    )