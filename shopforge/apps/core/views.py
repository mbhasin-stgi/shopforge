"""
Core views that serve the SPA shell.

These views just render a template — Vue takes over from there.
The template includes the Vite bundle which bootstraps the Vue app.
"""

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView


@method_decorator(ensure_csrf_cookie, name="dispatch")
class AppView(TemplateView):
    """
    Serve the main SPA shell.

    Any URL that doesn't match an API route gets this template.
    Vue Router handles client-side routing from there.
    The ensure_csrf_cookie decorator forces Django to set the csrftoken cookie
    on every GET so Vue/axios can read it for subsequent API calls.
    """

    template_name = "pages/app.html"


@method_decorator(ensure_csrf_cookie, name="dispatch")
class LoginView(TemplateView):
    """Serve the login page (separate entry point, smaller bundle)."""

    template_name = "pages/login.html"
