"""
Production settings for ShopForge.

Security-hardened, performance-optimized, monitoring-enabled.
All secrets come from environment variables — NOTHING is hardcoded.
"""

from .base import *  # noqa: F401, F403
from .base import env

# ============================================================
# SECURITY
# ============================================================
DEBUG = False

SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

# HTTPS enforcement
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# ============================================================
# DATABASE (use connection pooling in production)
# ============================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB"),
        "USER": env("POSTGRES_USER"),
        "PASSWORD": env("POSTGRES_PASSWORD"),
        "HOST": env("POSTGRES_HOST"),
        "PORT": env("POSTGRES_PORT", default="5432"),
        "ATOMIC_REQUESTS": True,
        "CONN_MAX_AGE": 60,  # Keep connections alive for 60 seconds
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

# ============================================================
# STATIC FILES (served by WhiteNoise with far-future cache headers)
# ============================================================
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# S3 configuration for user-uploaded media
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default="us-east-1")
AWS_DEFAULT_ACL = "private"
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}

# ============================================================
# EMAIL (production SMTP)
# ============================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")

# ============================================================
# SENTRY (error monitoring)
# ============================================================
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,  # 10% of requests are traced for performance
        send_default_pii=False,  # NEVER send personally identifiable information
        environment="production",
    )

# ============================================================
# LOGGING (structured for log aggregation)
# ============================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "django.utils.log.ServerFormatter",
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "shopforge": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# ============================================================
# PERFORMANCE
# ============================================================
# Session stored in cache (Redis) — faster than database sessions
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Django Vite in production mode (reads from manifest)
DJANGO_VITE = {
    "default": {
        "dev_mode": False,
        "manifest_path": str(BASE_DIR / "shopforge" / "webapp" / "dist" / ".vite" / "manifest.json"),
    }
}
