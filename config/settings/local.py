"""
Local development settings for ShopForge.

- Debug mode enabled
- Django Debug Toolbar
- Console email backend
- Relaxed security
- Vite dev server integration
"""

import socket

from .base import *  # noqa: F401, F403
from .base import BASE_DIR, INSTALLED_APPS, MIDDLEWARE, env

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
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]

# ============================================================
# EMAIL — MailHog SMTP (view at http://localhost:8025)
# MailHog catches all outgoing mail without actually delivering it.
# ============================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "mailhog"  # Docker service name — resolves inside the network
EMAIL_PORT = 1025
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

# ============================================================
# DJANGO VITE (frontend dev server)
# ============================================================
DJANGO_VITE = {
    "default": {
        "dev_mode": True,
        "dev_server_host": env("DJANGO_VITE_DEV_SERVER_HOST", default="localhost"),
        "dev_server_port": env("DJANGO_VITE_DEV_SERVER_PORT", default="5174"),
        # django-vite 3.x prepends urljoin(STATIC_URL, static_url_prefix) to every
        # dev-server URL. Setting "/" makes urljoin("/static/", "/") → "/", which
        # strips the unwanted /static/ prefix so URLs stay at http://localhost:5174/...
        "static_url_prefix": "/",
    }
}

# ============================================================
# CACHING (use Redis even in local — matches production)
# ============================================================
# Keep the Redis cache from base.py. Some devs prefer LocMemCache
# for faster tests, but Redis in local catches config issues early.

# ============================================================
# CORS: allow Vite dev server to call Django API
# ============================================================
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
CORS_ALLOW_CREDENTIALS = True

# ============================================================
# CELERY (eager mode — tasks execute immediately, no worker needed for quick testing)
# ============================================================
# Uncomment if you want tasks to run synchronously during development:
# CELERY_TASK_ALWAYS_EAGER = True
# CELERY_TASK_EAGER_PROPAGATES = True

# ============================================================
# STATIC FILES — use simple storage in dev (no manifest required)
# CompressedManifestStaticFilesStorage from base.py requires collectstatic
# to have been run. Override here so the dev server starts without it.
# ============================================================
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Only include the Vite dist directory if it has been built.
# In dev mode we use the Vite dev server, so the dist dir is not needed.
STATICFILES_DIRS = [
    BASE_DIR / "shopforge" / "static",
]
