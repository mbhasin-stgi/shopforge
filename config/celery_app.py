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
    # Check for low stock every hour
    "check-low-stock-hourly": {
        "task": "shopforge.apps.inventory.tasks.check_low_stock",
        "schedule": crontab(minute=0),  # Every hour, on the hour
    },
    # Send daily order summary to admin
    "daily-order-summary": {
        "task": "shopforge.apps.orders.tasks.send_daily_order_summary",
        "schedule": crontab(hour=8, minute=0),  # Every day at 8 AM
    },
    # Clean up expired cart sessions weekly
    "cleanup-expired-sessions": {
        "task": "shopforge.apps.orders.tasks.cleanup_expired_carts",
        "schedule": crontab(hour=3, minute=0, day_of_week="sunday"),  # Sunday at 3 AM
    },
}
