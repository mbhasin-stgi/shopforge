"""
Celery tasks for the Orders app.

Each task is a standalone function decorated with @shared_task.
They receive simple arguments (IDs, strings, numbers) — never model instances
(those can't be serialized to JSON).
"""

import logging

from celery import shared_task

from django.conf import settings
from django.core.mail import send_mail
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

    Runs every day at 8 AM (configured in beat_schedule).
    """
    from shopforge.apps.orders.models import Order

    yesterday = timezone.now() - timezone.timedelta(days=1)
    orders_today = Order.objects.filter(created_at__gte=yesterday)

    summary = {
        "total_orders": orders_today.count(),
        "total_revenue": sum(o.total for o in orders_today),
        "pending": orders_today.filter(status=Order.Status.PENDING).count(),
        "confirmed": orders_today.filter(status=Order.Status.CONFIRMED).count(),
    }

    send_mail(
        subject=f"ShopForge Daily Summary: {summary['total_orders']} orders, ${summary['total_revenue']}",
        message=f"Orders: {summary['total_orders']}\nRevenue: ${summary['total_revenue']}\nPending: {summary['pending']}\nConfirmed: {summary['confirmed']}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        fail_silently=True,
    )


@shared_task
def cleanup_expired_carts():
    """Remove cart sessions older than 7 days."""
    # Placeholder for cart cleanup logic
    logger.info("Expired cart cleanup completed.")
