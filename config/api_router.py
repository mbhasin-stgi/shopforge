"""API URL Configuration for ShopForge."""

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from django.urls import include, path

from shopforge.apps.core.api.dashboard import (
    DashboardLowStockView,
    DashboardRevenueChartView,
    DashboardStatsView,
    DashboardTopProductsView,
)
from shopforge.apps.core.api.views import health_check

app_name = "api"

urlpatterns = [
    # Health check — used by Docker HEALTHCHECK and load balancers
    path("health/", health_check, name="health-check"),
    # Product catalog (categories nested under products, reviews nested under products)
    path("products/", include("shopforge.apps.products.api.urls", namespace="products")),
    # Order management
    path("orders/", include("shopforge.apps.orders.api.urls", namespace="orders")),
    # User accounts
    path("users/", include("shopforge.apps.users.api.urls", namespace="users")),
    # Inventory (admin)
    path("inventory/", include("shopforge.apps.inventory.api.urls", namespace="inventory")),
    # Shopping cart (DB-backed)
    path("cart/", include("shopforge.apps.cart.api.urls", namespace="cart")),
    # Saved shipping addresses
    path("addresses/", include("shopforge.apps.addresses.api.urls", namespace="addresses")),
    # Wishlist
    path("wishlist/", include("shopforge.apps.wishlist.api.urls", namespace="wishlist")),
    # Coupons
    path("coupons/", include("shopforge.apps.coupons.api.urls", namespace="coupons")),
    # Admin dashboard analytics
    path("admin/dashboard/stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("admin/dashboard/top-products/", DashboardTopProductsView.as_view(), name="dashboard-top-products"),
    path("admin/dashboard/low-stock/", DashboardLowStockView.as_view(), name="dashboard-low-stock"),
    path("admin/dashboard/revenue-chart/", DashboardRevenueChartView.as_view(), name="dashboard-revenue-chart"),
    # Authentication (login, logout, password change/reset)
    path("auth/", include("dj_rest_auth.urls")),
    # Registration (sign-up + email verification)
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    # OpenAPI Schema
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("schema/swagger-ui/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="swagger-ui"),
    path("schema/redoc/", SpectacularRedocView.as_view(url_name="api:schema"), name="redoc"),
]
