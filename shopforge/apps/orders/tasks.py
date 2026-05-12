"""
Celery tasks for the Orders app.

Each task is a standalone function decorated with @shared_task.
They receive simple arguments (IDs, strings, numbers) — never model instances
(those can't be serialized to JSON).
"""

import logging
from datetime import timedelta

from celery import shared_task

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db.models import Count, Sum
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
)
def send_order_confirmation_email(self, order_id):
    """
    Send order confirmation email to the customer.

    Args:
        order_id: UUID of the order (as string — UUIDs are JSON-serializable)

    The bind=True gives us `self` — used for retrying.
    autoretry_for=(Exception,) means ANY exception triggers a retry.
    retry_backoff=True means delays increase: 60s, 120s, 240s (exponential).
    """
    from shopforge.apps.orders.models import Order

    try:
        order = Order.objects.select_related("customer").prefetch_related("items").get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found. Cannot send confirmation email.")
        return  # Don't retry — the order genuinely doesn't exist

    context = {
        "order": order,
        "items": order.items.all(),
        "customer_name": order.customer.full_name,
    }

    subject = f"Order Confirmed: {order.order_number}"
    html_message = render_to_string("emails/order_confirmation.html", context)
    plain_message = render_to_string("emails/order_confirmation.txt", context)

    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.customer.email],
        fail_silently=False,  # Let it raise so autoretry can catch it
    )

    logger.info(f"Order confirmation email sent for {order.order_number}")


@shared_task
def send_daily_order_summary():
    """
    Send daily summary of orders to admin.

    Runs every day at 8 AM (configured in celery_app.py beat_schedule).
    Uses DB aggregation instead of iterating all orders to avoid OOM on large datasets.
    """
    from shopforge.apps.orders.models import Order

    since = timezone.now() - timedelta(days=1)
    qs = Order.objects.filter(created_at__gte=since)

    agg = qs.aggregate(total_orders=Count("id"), total_revenue=Sum("total"))
    total_orders = agg["total_orders"] or 0
    total_revenue = agg["total_revenue"] or 0

    status_counts = {status: qs.filter(status=status).count() for status in Order.Status.values}

    lines = "\n".join(f"  {label}: {status_counts[val]}" for val, label in Order.Status.choices)
    message = f"Orders (last 24h): {total_orders}\n" f"Revenue: ${total_revenue:.2f}\n\n" f"By status:\n{lines}"

    send_mail(
        subject=f"ShopForge Daily Summary: {total_orders} orders, ${total_revenue:.2f}",
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        fail_silently=True,
    )


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_shipping_notification(self, order_id: str) -> None:
    """Send a shipping notification email to the customer."""
    from shopforge.apps.orders.models import Order

    try:
        order = Order.objects.select_related("customer").prefetch_related("items").get(id=order_id)
    except Order.DoesNotExist:
        logger.error("Order %s not found for shipping notification.", order_id)
        return

    site_url = getattr(settings, "SITE_URL", "http://localhost:8000")
    context = {"order": order, "site_url": site_url}
    subject = f"Your ShopForge order {order.order_number} has shipped!"

    text_body = render_to_string("emails/order_shipped.txt", context)
    html_body = render_to_string("emails/order_shipped.html", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[order.customer.email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()
    logger.info("Shipping notification sent for order %s", order.order_number)


@shared_task
def cleanup_stale_pending_orders():
    """
    Cancel PENDING orders that have not progressed to CONFIRMED within 24 hours.

    This prevents ghost reservations from tying up stock indefinitely.
    Runs daily. Stock release is handled automatically by the pre_save signal
    in orders/signals.py when the status changes to CANCELLED.
    """
    from django.db import transaction

    from shopforge.apps.orders.models import Order

    cutoff = timezone.now() - timedelta(hours=24)
    stale_orders = Order.objects.filter(
        status=Order.Status.PENDING,
        created_at__lt=cutoff,
    )

    cancelled_count = 0
    for order in stale_orders:
        with transaction.atomic():
            order.status = Order.Status.CANCELLED
            order.save(update_fields=["status", "updated_at"])
        cancelled_count += 1

    if cancelled_count:
        logger.info("Auto-cancelled %d stale pending orders.", cancelled_count)
    else:
        logger.info("No stale pending orders found.")
