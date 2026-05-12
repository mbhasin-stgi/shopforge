"""
Order service layer.

OrderService encapsulates the full order-creation workflow so that both:
- Direct order creation (POST /api/orders/)
- Cart checkout (POST /api/cart/checkout/)

share the same atomic business logic.
"""

import logging

from django.db import transaction

from shopforge.apps.inventory.services import InventoryService
from shopforge.apps.orders.models import Order, OrderItem

logger = logging.getLogger(__name__)


class OrderService:
    """Service for order operations."""

    @staticmethod
    @transaction.atomic
    def create_order(customer, items_data: list[dict], shipping_data: dict) -> Order:
        """
        Create a new order from a list of {product, quantity} dicts.

        Steps (all in one DB transaction):
        1. Lock and validate stock for every item.
        2. Create the Order record.
        3. Create OrderItem records with price snapshots.
        4. Reserve stock via InventoryService.
        5. Calculate order totals.

        After the transaction commits:
        6. Fire async order confirmation email.

        Raises ValueError if any product is out of stock.
        """
        from shopforge.apps.inventory.models import StockRecord

        # Validate stock and collect products before mutating anything
        validated = []
        for entry in items_data:
            product = entry["product"]
            qty = entry["quantity"]
            try:
                StockRecord.objects.select_for_update().get(product=product)
            except StockRecord.DoesNotExist:
                raise ValueError(f"No stock record found for '{product.name}'.")
            available = product.stock.quantity - product.stock.reserved_quantity
            if available < qty:
                raise ValueError(
                    f"Insufficient stock for '{product.name}': " f"requested {qty}, available {available}."
                )
            validated.append((product, qty))

        # Create the order shell
        shipping_fields = {k: v for k, v in shipping_data.items() if k != "coupon_code"}
        order = Order.objects.create(customer=customer, **shipping_fields)

        # Apply coupon discount if provided
        coupon_code = shipping_data.get("coupon_code", "")
        if coupon_code:
            try:
                from shopforge.apps.coupons.services import CouponService

                discount = CouponService.validate_and_apply(coupon_code, customer, order)
                order.discount_amount = discount
                order.save(update_fields=["discount_amount"])
            except Exception as exc:
                logger.warning("Coupon '%s' could not be applied: %s", coupon_code, exc)

        # Create line items and reserve stock atomically
        for product, qty in validated:
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_sku=product.sku,
                price_at_purchase=product.price,
                quantity=qty,
            )
            InventoryService.reserve(
                product=product,
                quantity=qty,
                order_number=order.order_number,
            )

        order.calculate_totals()

        # Fire async email after transaction commits (sees committed data)
        transaction.on_commit(lambda: _fire_confirmation_email(str(order.id)))

        return order

    @staticmethod
    def create_from_cart(cart, customer, shipping_data: dict) -> Order:
        """
        Convert a Cart into an Order.

        Delegates to create_order() after translating cart items.
        Cart is NOT cleared here — caller (CartViewSet) clears it after success.
        """
        items_data = [
            {"product": item.product, "quantity": item.quantity} for item in cart.items.select_related("product").all()
        ]
        if not items_data:
            raise ValueError("Cannot checkout an empty cart.")
        return OrderService.create_order(customer, items_data, shipping_data)


def _fire_confirmation_email(order_id: str) -> None:
    """Helper to fire the confirmation email task after transaction commit."""
    from shopforge.apps.orders.tasks import send_order_confirmation_email

    send_order_confirmation_email.delay(order_id)
