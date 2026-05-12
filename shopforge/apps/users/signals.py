"""User signals — welcome email on registration."""

import logging

from allauth.account.signals import user_signed_up

from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(user_signed_up)
def send_welcome_email_on_signup(sender, request, user, **kwargs):
    """Send a welcome email after successful registration via allauth."""
    from django.conf import settings
    from django.core.mail import EmailMultiAlternatives
    from django.template.loader import render_to_string

    site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
    context = {"user": user, "site_url": site_url}

    text_body = render_to_string("emails/welcome.txt", context)
    html_body = render_to_string("emails/welcome.html", context)

    msg = EmailMultiAlternatives(
        subject="Welcome to ShopForge!",
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    msg.attach_alternative(html_body, "text/html")
    try:
        msg.send()
        logger.info("Welcome email sent to %s", user.email)
    except Exception as exc:
        logger.error("Failed to send welcome email to %s: %s", user.email, exc)
