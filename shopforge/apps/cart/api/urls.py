"""Cart API URL configuration."""

from rest_framework.routers import DefaultRouter

from shopforge.apps.cart.api.views import CartViewSet

app_name = "cart"

router = DefaultRouter()
router.register("", CartViewSet, basename="cart")

urlpatterns = router.urls
