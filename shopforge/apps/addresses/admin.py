from django.contrib import admin

from shopforge.apps.addresses.models import UserAddress


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ("user", "label", "full_name", "city", "country", "is_default")
    list_filter = ("country", "is_default")
    search_fields = ("user__email", "full_name", "city", "postal_code")
    readonly_fields = ("id", "created_at", "updated_at")
