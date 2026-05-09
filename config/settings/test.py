"""
Test settings for ShopForge.

Optimized for speed:
- Faster password hasher
- In-memory cache
- Disabled throttling
- Synchronous Celery tasks
"""

import tempfile

from .base import *  # noqa: F401, F403
from .base import REST_FRAMEWORK, env

# ============================================================
# PASSWORD HASHING (fast for tests, insecure for production)
# ============================================================
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# ============================================================
# CACHE (in-memory, no Redis needed for tests)
# ============================================================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# ============================================================
# EMAIL (in-memory backend for test assertions)
# ============================================================
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

for template in TEMPLATES:
    template["OPTIONS"]["debug"] = False

# ============================================================
# CELERY (run tasks synchronously in tests)
# ============================================================
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# ============================================================
# THROTTLING (disabled — tests shouldn't fail due to rate limits)
# ============================================================
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {}

# ============================================================
# MEDIA (use temp directory for test file uploads)
# ============================================================
MEDIA_ROOT = tempfile.mkdtemp()

# ============================================================
# LOGGING (quieter during tests)
# ============================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
        "level": "CRITICAL",
    },
}

# ============================================================
# SECURITY (relaxed for tests)
# ============================================================
SECRET_KEY = env("DJANGO_SECRET_KEY", default="test-key")

# ============================================================
# MISC
# ============================================================
# Don't send emails to Sentry during tests
SENTRY_DSN = None
