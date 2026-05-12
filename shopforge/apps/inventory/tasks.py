"""Celery tasks for inventory management."""

import logging

from celery import shared_task

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import F

logger = logging.getLogger(__name__)


@shared_task
def check_low_stock():
    """
    Check all products for low stock levels based on available (not raw) quantity.

    Runs hourly via Celery Beat. Sends alert email when any products fall at or
    below their reorder threshold.
    """
    from shopforge.apps.inventory.models import StockRecord

    # Use available_quantity (quantity - reserved) for the threshold check,
    # consistent with StockRecord.needs_reorder property.
    all_records = StockRecord.objects.select_related("product").annotate(
        computed_available=F("quantity") - F("reserved_quantity")
    )
    low_stock_items = [r for r in all_records if r.computed_available <= r.reorder_level]

    if not low_stock_items:
        logger.info("All stock levels healthy.")
        return

    items_list = "\n".join(
        f"- {item.product.name}: {item.available_quantity} available "
        f"(reorder threshold: {item.reorder_level}, suggest ordering: {item.reorder_quantity})"
        for item in low_stock_items
    )

    send_mail(
        subject=f"Low Stock Alert: {len(low_stock_items)} product(s) need reordering",
        message=f"The following products are at or below their reorder level:\n\n{items_list}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        fail_silently=True,
    )

    logger.warning("Low stock alert sent for %d item(s).", len(low_stock_items))


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def fulfill_order_stock(self, order_id):
    """
    Deduct actual stock quantity once an order is fulfilled/shipped.

    Stock is *reserved* synchronously at order creation time. This task converts
    reserved stock into an actual deduction (SOLD movement) when the order ships.
    It is idempotent: if a SOLD movement already exists for this order it skips.
    """
    from django.db import transaction

    from shopforge.apps.inventory.models import StockMovement, StockRecord
    from shopforge.apps.orders.models import Order

    try:
        order = Order.objects.prefetch_related("items__product").get(id=order_id)
    except Order.DoesNotExist:
        logger.error("Order %s not found for fulfillment.", order_id)
        return

    with transaction.atomic():
        for item in order.items.all():
            try:
                stock = StockRecord.objects.select_for_update().get(product=item.product)
            except StockRecord.DoesNotExist:
                logger.error("StockRecord missing for product %s", item.product_id)
                continue

            # Idempotency: skip if a SOLD movement already exists for this order
            already_fulfilled = StockMovement.objects.filter(
                stock_record=stock,
                movement_type=StockMovement.MovementType.SOLD,
                reference=order.order_number,
            ).exists()
            if already_fulfilled:
                continue

            # Convert reservation to actual sale
            deduct = min(item.quantity, stock.reserved_quantity)
            stock.quantity -= item.quantity
            stock.reserved_quantity -= deduct
            stock.save(update_fields=["quantity", "reserved_quantity", "updated_at"])

            StockMovement.objects.create(
                stock_record=stock,
                movement_type=StockMovement.MovementType.SOLD,
                quantity_change=-item.quantity,
                reference=order.order_number,
                notes=f"Fulfilled on shipment of order {order.order_number}",
            )

    logger.info("Stock fulfilled for order %s", order.order_number)
