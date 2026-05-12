"""
Order signals — react to order status transitions.

Connected in OrdersConfig.ready() to avoid circular imports.
"""

import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(pre_save, sender="orders.Order")
def handle_order_status_change(sender, instance, **kwargs):
    """
    Fire side-effects when an order's status changes.

    - SHIPPED  → queue fulfillment stock deduction + shipping notification email
    - CANCELLED → release reserved stock via InventoryService
    """
    if not instance.pk:
        return  # New order — no previous state

    try:
        previous = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    if previous.status == instance.status:
        return  # No status change

    _on_status_change(previous.status, instance.status, instance)


def _on_status_change(old_status, new_status, order) -> None:
    """Dispatch side-effects based on the status transition."""
    from shopforge.apps.orders.models import Order

    if new_status == Order.Status.SHIPPED:
        _handle_shipped(order)
    elif new_status == Order.Status.CANCELLED and old_status not in (
        Order.Status.CANCELLED,
        Order.Status.REFUNDED,
    ):
        _handle_cancelled(order)


def _handle_shipped(order) -> None:
    """Deduct stock (SOLD movement) and notify customer when order ships."""
    from shopforge.apps.inventory.tasks import fulfill_order_stock
    from shopforge.apps.orders.tasks import send_shipping_notification

    fulfill_order_stock.delay(str(order.id))
    send_shipping_notification.delay(str(order.id))
    logger.info("Queued fulfill_order_stock + shipping notification for order %s", order.order_number)


def _handle_cancelled(order) -> None:
    """Release reserved stock when an order is cancelled via the signal path."""
    from shopforge.apps.inventory.services import InventoryService

    for item in order.items.select_related("product").all():
        try:
            InventoryService.release(
                product=item.product,
                quantity=item.quantity,
                order_number=order.order_number,
            )
        except Exception as exc:
            logger.error(
                "Failed to release stock for %s on cancellation of %s: %s",
                item.product.name,
                order.order_number,
                exc,
            )
