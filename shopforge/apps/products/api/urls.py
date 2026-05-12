"""URL configuration for the Products API."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductViewSet

app_name = "products"

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("", ProductViewSet, basename="product")

# Nested reviews: /api/products/{product_slug}/reviews/
urlpatterns = router.urls + [
    path(
        "<slug:product_slug>/reviews/",
        include("shopforge.apps.reviews.api.urls", namespace="reviews"),
    ),
]
