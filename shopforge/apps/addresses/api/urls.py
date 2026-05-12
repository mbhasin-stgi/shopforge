"""Address API URL configuration."""

from rest_framework.routers import DefaultRouter

from shopforge.apps.addresses.api.views import UserAddressViewSet

app_name = "addresses"

router = DefaultRouter()
router.register("", UserAddressViewSet, basename="address")

urlpatterns = router.urls
