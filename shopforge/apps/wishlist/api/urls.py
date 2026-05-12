"""Wishlist API URL configuration."""

from rest_framework.routers import DefaultRouter

from shopforge.apps.wishlist.api.views import WishlistViewSet

app_name = "wishlist"

router = DefaultRouter()
router.register("", WishlistViewSet, basename="wishlist")

urlpatterns = router.urls
