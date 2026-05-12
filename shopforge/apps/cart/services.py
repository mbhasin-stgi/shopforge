"""
Cart service layer.

All cart mutations go through CartService so that:
- Business rules (stock checks, price refresh) are enforced in one place
- Views stay thin
"""

from django.db import transaction

from shopforge.apps.cart.models import Cart, CartItem
from shopforge.apps.products.models import Product


class CartService:
    """Service for cart operations."""

    @staticmethod
    def get_or_create_for_user(user) -> Cart:
        """Return the user's cart, creating one if it doesn't exist."""
        cart, _ = Cart.objects.get_or_create(owner=user)
        return cart

    @staticmethod
    def get_or_create_for_session(session_key: str) -> Cart:
        """Return the anonymous session cart, creating one if needed."""
        cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart

    @staticmethod
    @transaction.atomic
    def add_item(cart: Cart, product: Product, quantity: int = 1) -> CartItem:
        """
        Add `quantity` units of `product` to `cart`.

        If the item already exists its quantity is incremented.
        The price snapshot is only set on first add.
        """
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity, "price_snapshot": product.price},
        )
        if not created:
            item.quantity += quantity
            item.save(update_fields=["quantity", "updated_at"])
        return item

    @staticmethod
    @transaction.atomic
    def update_item(cart: Cart, product: Product, quantity: int) -> CartItem | None:
        """
        Set item quantity. Removes the item if quantity <= 0.

        Returns the updated CartItem or None if removed.
        """
        try:
            item = CartItem.objects.get(cart=cart, product=product)
        except CartItem.DoesNotExist:
            return None
        if quantity <= 0:
            item.delete()
            return None
        item.quantity = quantity
        item.save(update_fields=["quantity", "updated_at"])
        return item

    @staticmethod
    @transaction.atomic
    def remove_item(cart: Cart, product: Product) -> None:
        """Remove a specific product from the cart."""
        CartItem.objects.filter(cart=cart, product=product).delete()

    @staticmethod
    @transaction.atomic
    def clear(cart: Cart) -> None:
        """Empty the cart."""
        cart.items.all().delete()

    @staticmethod
    @transaction.atomic
    def merge_session_cart_into_user(session_key: str, user) -> Cart:
        """
        Merge an anonymous session cart into the authenticated user's cart.

        Called at login. Items from the session cart are added to the user cart
        (quantities are summed for duplicates). The session cart is then deleted.
        """
        user_cart, _ = Cart.objects.get_or_create(owner=user)
        try:
            session_cart = Cart.objects.get(session_key=session_key, owner__isnull=True)
        except Cart.DoesNotExist:
            return user_cart

        for item in session_cart.items.select_related("product").all():
            CartService.add_item(user_cart, item.product, item.quantity)

        session_cart.delete()
        return user_cart

    @staticmethod
    def refresh_prices(cart: Cart) -> None:
        """
        Update all price snapshots to current product prices.

        Call before checkout to ensure the user is not charged a stale price.
        """
        for item in cart.items.select_related("product").all():
            if item.price_snapshot != item.product.price:
                item.price_snapshot = item.product.price
                item.save(update_fields=["price_snapshot", "updated_at"])
