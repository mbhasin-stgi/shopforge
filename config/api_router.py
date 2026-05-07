"""API URL Configuration for ShopForge."""
from django.urls import include, path

app_name = "api"

urlpatterns = [
    # # Product catalog
    # path("products/", include("shopforge.apps.products.api.urls", namespace="products")),
    # # Order management
    # path("orders/", include("shopforge.apps.orders.api.urls", namespace="orders")),
    # # User accounts
    # path("users/", include("shopforge.apps.users.api.urls", namespace="users")),
    # # Inventory
    # path("inventory/", include("shopforge.apps.inventory.api.urls", namespace="inventory")),
    # # Authentication
    # path("auth/", include("dj_rest_auth.urls")),
    # # OpenAPI Schema
    # path("schema/", include("drf_spectacular.urls")),
]
