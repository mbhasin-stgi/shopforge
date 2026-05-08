"""ShopForge URL Configuration."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),
    # API routes (DRF)
    path("api/", include("config.api_router", namespace="api")),
    # Health check endpoint (for load balancers / k8s probes)
    path(
        "health/",
        TemplateView.as_view(template_name="health.html", content_type="text/plain"),
        name="health-check",
    ),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

    # Django Debug Toolbar
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
