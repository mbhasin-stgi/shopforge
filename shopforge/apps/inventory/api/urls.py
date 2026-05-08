"""URL configuration for the Inventory API."""

from rest_framework.routers import DefaultRouter

from .views import StockRecordViewSet

app_name = "inventory"

router = DefaultRouter()
router.register("", StockRecordViewSet, basename="stock")

urlpatterns = router.urls
