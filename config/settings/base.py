"""
Base settings for ShopForge.

These settings are shared across all environments (local, test, production).
Environment-specific settings files import * from this module and override
only what differs.
"""

from pathlib import Path

import environ

# ============================================================
# PATH CONFIGURATION
# ============================================================
# Build paths inside the project like this: BASE_DIR / 'subdir'
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # → /app (project root)
ROOT_DIR = BASE_DIR  # Alias used by some utilities

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================
env = environ.Env(
    # Default values for environment variables
    DJANGO_DEBUG=(bool, False),
    DJANGO_SECRET_KEY=(str, "CHANGE-ME-IN-PRODUCTION"),
    DJANGO_ALLOWED_HOSTS=(list, ["localhost"]),
)

# ============================================================
# CORE SETTINGS
# ============================================================
DEBUG = env("DJANGO_DEBUG")
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

# ============================================================
# APPLICATION DEFINITION
# ============================================================
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework.authtoken",
    "django_filters",
    "corsheaders",
    "django_extensions",
    "drf_spectacular",
    "django_celery_beat",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "django_vite",
]

LOCAL_APPS = [
    "shopforge.apps.users",
    "shopforge.apps.products",
    "shopforge.apps.orders",
    "shopforge.apps.inventory",
]

# The order matters! Django apps first, then third-party, then local.
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ============================================================
# MIDDLEWARE
# ============================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Static files (before all others)
    "corsheaders.middleware.CorsMiddleware",  # CORS (must be high up)
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# ============================================================
# URL CONFIGURATION
# ============================================================
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# ============================================================
# TEMPLATES
# ============================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(BASE_DIR / "shopforge" / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ============================================================
# DATABASE
# ============================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", default="shopforge"),
        "USER": env("POSTGRES_USER", default="shopforge"),
        "PASSWORD": env("POSTGRES_PASSWORD", default="shopforge_dev_password"),
        "HOST": env("POSTGRES_HOST", default="postgres"),
        "PORT": env("POSTGRES_PORT", default="5432"),
        "ATOMIC_REQUESTS": True,  # Wrap each request in a transaction
    }
}

# ============================================================
# AUTHENTICATION
# ============================================================
AUTH_USER_MODEL = "users.User"  # Custom user model (ALWAYS do this from day 1!)

# ─── django-allauth: email-only authentication ──────────────────────────────
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "none"  # Disable mandatory email confirmation in dev

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ============================================================
# INTERNATIONALIZATION
# ============================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True  # ALWAYS store datetimes in UTC

# ============================================================
# STATIC & MEDIA FILES
# ============================================================
STATIC_URL = "/static/"
STATIC_ROOT = str(BASE_DIR / "staticfiles")

MEDIA_URL = "/media/"
MEDIA_ROOT = str(BASE_DIR / "media")

# WhiteNoise for static file serving
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# ============================================================
# DEFAULT PRIMARY KEY TYPE
# ============================================================
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}

# ============================================================
# DRF SPECTACULAR (OpenAPI Schema)
# ============================================================
SPECTACULAR_SETTINGS = {
    "TITLE": "ShopForge API",
    "DESCRIPTION": "Corporate-grade e-commerce platform API",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

# ============================================================
# CELERY CONFIGURATION
# ============================================================
CELERY_BROKER_URL = env("REDIS_URL", default="redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("REDIS_URL", default="redis://redis:6379/0")

# Serialization: JSON is safer than pickle (no arbitrary code execution)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# Timezone
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# Task behavior
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes soft limit (raises exception)
CELERY_TASK_ACKS_LATE = True  # Acknowledge AFTER task completes (safer for retries)
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Don't prefetch tasks (fairer distribution)

# Retry policy
CELERY_TASK_DEFAULT_RETRY_DELAY = 60  # Wait 60s before retrying
CELERY_TASK_MAX_RETRIES = 3

# Result expiration (don't keep results forever)
CELERY_RESULT_EXPIRES = 60 * 60 * 24  # 24 hours

# ─── Task Routing ────────────────────────────────────────────────────
CELERY_TASK_ROUTES = {
    "shopforge.apps.orders.tasks.send_order_confirmation_email": {"queue": "emails"},
    "shopforge.apps.orders.tasks.send_daily_order_summary": {"queue": "emails"},
    "shopforge.apps.inventory.tasks.*": {"queue": "inventory"},
}
CELERY_TASK_DEFAULT_QUEUE = "default"


# ============================================================
# REDIS / CACHING
# ============================================================
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://redis:6379/0"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# ============================================================
# EMAIL
# ============================================================
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="mailhog")
EMAIL_PORT = env.int("EMAIL_PORT", default=1025)
DEFAULT_FROM_EMAIL = "ShopForge <noreply@shopforge.dev>"

# ADMINS receive error emails and daily summaries.
# Override in production via env var: DJANGO_ADMIN_EMAIL=ops@yourcompany.com
ADMIN_EMAIL = env("DJANGO_ADMIN_EMAIL", default="admin@shopforge.dev")
ADMINS = [("ShopForge Admin", ADMIN_EMAIL)]

# ============================================================
# SECURITY (base — production.py tightens these further)
# ============================================================
SESSION_COOKIE_HTTPONLY = True
# CSRF cookie must NOT be HttpOnly — JavaScript (axios) reads it to send as
# X-CSRFToken header on every POST/PUT/PATCH/DELETE request.
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = "DENY"

# ============================================================
# SITES FRAMEWORK
# ============================================================
SITE_ID = 1

# ============================================================
# LOGGING
# ============================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "shopforge": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

# ─── Django Vite ─────────────────────────────────────────────────────
DJANGO_VITE = {
    "default": {
        "dev_mode": DEBUG,
        "dev_server_host": "localhost",
        "dev_server_port": 5174,
        "manifest_path": BASE_DIR / "shopforge" / "webapp" / "dist" / "manifest.json",
        "static_url_prefix": "webapp/dist",
    }
}

# Static files — Vite builds go into the static directory
STATICFILES_DIRS = [
    BASE_DIR / "shopforge" / "webapp" / "dist",
    BASE_DIR / "shopforge" / "static",
]
