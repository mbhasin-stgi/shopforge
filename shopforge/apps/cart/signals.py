"""Cart signals — merge anonymous session cart into user cart on login."""

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    """Merge anonymous session cart into the logged-in user's cart."""
    session_key = request.session.session_key
    if not session_key:
        return
    from shopforge.apps.cart.services import CartService

    CartService.merge_session_cart_into_user(session_key, user)
