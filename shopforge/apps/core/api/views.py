"""Health check endpoint for load balancers and Docker HEALTHCHECK."""

from django.core.cache import cache
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Liveness + readiness health check.

    Returns HTTP 200 when Django, PostgreSQL, and Redis are all reachable.
    Returns HTTP 503 with a JSON body describing which check failed.

    Used by: Docker HEALTHCHECK directive, load balancers, uptime monitors.
    """
    health = {"status": "healthy", "checks": {}}

    # ── Database check ────────────────────────────────────────────────
    try:
        connection.ensure_connection()
        health["checks"]["database"] = "ok"
    except Exception as exc:
        health["checks"]["database"] = f"error: {exc}"
        health["status"] = "unhealthy"

    # ── Cache / Redis check ───────────────────────────────────────────
    try:
        cache.set("health_check", "ok", timeout=10)
        value = cache.get("health_check")
        if value == "ok":
            health["checks"]["cache"] = "ok"
        else:
            health["checks"]["cache"] = "error: read-back failed"
            health["status"] = "unhealthy"
    except Exception as exc:
        health["checks"]["cache"] = f"error: {exc}"
        health["status"] = "unhealthy"

    status_code = 200 if health["status"] == "healthy" else 503
    return Response(health, status=status_code)
