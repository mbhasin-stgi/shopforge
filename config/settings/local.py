"""
Local development settings for ShopForge.

- Debug mode enabled
- Django Debug Toolbar
- Console email backend
- Relaxed security
- Vite dev server integration
"""
from .base import *  # noqa: F401, F403
from .base import INSTALLED_APPS, MIDDLEWARE, env

# ============================================================
# DEBUG
# ============================================================
DEBUG = True

# ============================================================
# ALLOWED HOSTS (permissive for local dev)
# ============================================================
ALLOWED_HOSTS = ["*"]

# ============================================================
# INSTALLED APPS (add dev-only apps)
# ============================================================
INSTALLED_APPS += [
    "debug_toolbar",
    "django_vite",
]

# ============================================================
# MIDDLEWARE (add debug toolbar)
# ============================================================
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

# ============================================================
# DEBUG TOOLBAR
# ============================================================
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]

# Docker-compatible internal IPs detection
import socket

hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]

# ============================================================
# EMAIL (use console backend — see emails in terminal output)
# ============================================================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ============================================================
# DJANGO VITE (frontend dev server)
# ============================================================
DJANGO_VITE = {
    "default": {
        "dev_mode": True,
        "dev_server_host": env("DJANGO_VITE_DEV_SERVER_HOST", default="localhost"),
        "dev_server_port": env("DJANGO_VITE_DEV_SERVER_PORT", default="5174"),
    }
}

# ============================================================
# CACHING (use Redis even in local — matches production)
# ============================================================
# Keep the Redis cache from base.py. Some devs prefer LocMemCache
# for faster tests, but Redis in local catches config issues early.

# ============================================================
# CORS (allow everything in local dev)
# ============================================================
CORS_ALLOW_ALL_ORIGINS = True

# ============================================================
# CELERY (eager mode — tasks execute immediately, no worker needed for quick testing)
# ============================================================
# Uncomment if you want tasks to run synchronously during development:
# CELERY_TASK_ALWAYS_EAGER = True
# CELERY_TASK_EAGER_PROPAGATES = True