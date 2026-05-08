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
    Check all products for low stock levels.

    Runs hourly. Sends alert email if any products need reordering.
    """
    from shopforge.apps.inventory.models import StockRecord

    low_stock_items = StockRecord.objects.select_related("product").filter(quantity__lte=F("reorder_level"))

    if not low_stock_items.exists():
        logger.info("All stock levels healthy.")
        return

    items_list = "\n".join(
        f"- {item.product.name}: {item.available_quantity} remaining (reorder at {item.reorder_level})"
        for item in low_stock_items
    )

    send_mail(
        subject=f"⚠️ Low Stock Alert: {low_stock_items.count()} items need reordering",
        message=f"The following items are below reorder level:\n\n{items_list}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        fail_silently=True,
    )

    logger.warning(f"Low stock alert sent for {low_stock_items.count()} items.")


@shared_task(bind=True, max_retries=3)
def reserve_stock_for_order(self, order_id):
    """
    Reserve inventory for a confirmed order.

    This is called after payment confirmation. It:
    1. Checks stock availability
    2. Decrements available stock
    3. Creates a StockMovement audit record
    """
    from django.db import transaction

    from shopforge.apps.inventory.models import StockMovement, StockRecord
    from shopforge.apps.orders.models import Order

    try:
        order = Order.objects.prefetch_related("items__product").get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found for stock reservation.")
        return

    with transaction.atomic():
        for item in order.items.all():
            stock = StockRecord.objects.select_for_update().get(product=item.product)

            if stock.available_quantity < item.quantity:
                logger.error(
                    f"Insufficient stock for {item.product.name}: "
                    f"need {item.quantity}, have {stock.available_quantity}"
                )
                raise self.retry(countdown=30)

            stock.reserved_quantity += item.quantity
            stock.save(update_fields=["reserved_quantity", "updated_at"])

            StockMovement.objects.create(
                stock_record=stock,
                movement_type=StockMovement.MovementType.RESERVED,
                quantity_change=-item.quantity,
                reference=order.order_number,
                notes=f"Reserved for order {order.order_number}",
            )

    logger.info(f"Stock reserved for order {order.order_number}")
