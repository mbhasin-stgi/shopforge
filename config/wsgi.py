"""
WSGI config for ShopForge.

It exposes the WSGI callable as a module-level variable named ``application``.
Gunicorn uses this in production: gunicorn config.wsgi:application
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()