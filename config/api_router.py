"""API URL Configuration for ShopForge."""

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from django.urls import include, path

from shopforge.apps.core.api.views import health_check

app_name = "api"

urlpatterns = [
    # Health check — used by Docker HEALTHCHECK and load balancers
    path("health/", health_check, name="health-check"),
    # Product catalog
    path("products/", include("shopforge.apps.products.api.urls", namespace="products")),
    # Order management
    path("orders/", include("shopforge.apps.orders.api.urls", namespace="orders")),
    # User accounts
    path("users/", include("shopforge.apps.users.api.urls", namespace="users")),
    # Inventory
    path("inventory/", include("shopforge.apps.inventory.api.urls", namespace="inventory")),
    # Authentication
    path("auth/", include("dj_rest_auth.urls")),
    # OpenAPI Schema
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="swagger-ui"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="api:schema"), name="redoc"),
]
