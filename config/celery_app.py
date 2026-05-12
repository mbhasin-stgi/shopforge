import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("shopforge")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related config keys
#   should have a `CELERY_` prefix in Django settings.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


app.conf.beat_schedule = {
    # Check for low stock every hour — alerts admin when products fall below reorder_level
    "check-low-stock-hourly": {
        "task": "shopforge.apps.inventory.tasks.check_low_stock",
        "schedule": crontab(minute=0),  # Top of every hour
    },
    # Send daily order summary to admin at 8 AM UTC
    "daily-order-summary": {
        "task": "shopforge.apps.orders.tasks.send_daily_order_summary",
        "schedule": crontab(hour=8, minute=0),
    },
    # Cancel stale PENDING orders (no payment within 24h) every night at 2 AM UTC
    "cleanup-stale-pending-orders": {
        "task": "shopforge.apps.orders.tasks.cleanup_stale_pending_orders",
        "schedule": crontab(hour=2, minute=0),
    },
}
