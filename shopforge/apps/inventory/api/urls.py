"""URL configuration for the Inventory API."""

from rest_framework.routers import DefaultRouter

from .views import StockMovementViewSet, StockRecordViewSet

app_name = "inventory"

router = DefaultRouter()
router.register("movements", StockMovementViewSet, basename="movement")
router.register("", StockRecordViewSet, basename="stock")

urlpatterns = router.urls
