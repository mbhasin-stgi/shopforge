"""Review URL configuration — registered as nested routes under products."""

from rest_framework.routers import DefaultRouter

from shopforge.apps.reviews.api.views import ReviewViewSet

app_name = "reviews"

router = DefaultRouter()
router.register("", ReviewViewSet, basename="review")

urlpatterns = router.urls
