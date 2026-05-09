# Background Tasks

ShopForge uses Celery with Redis as the message broker for all background processing.

## Task Queues

| Queue | Purpose | Tasks |
|-------|---------|-------|
| `emails` | Email delivery | Order confirmation, password reset |
| `inventory` | Stock management | Low-stock alerts, restock notifications |
| `default` | Everything else | General async work |

## Defining a Task

```python
# shopforge/apps/orders/tasks.py
from config.celery_app import app

@app.task(queue="emails", bind=True, max_retries=3)
def send_order_confirmation(self, order_id: int) -> None:
    """Send order confirmation email."""
    try:
        order = Order.objects.get(pk=order_id)
        # ... send email
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

## Calling a Task

```python
# Async (fire and forget)
send_order_confirmation.delay(order.id)

# With delay
send_order_confirmation.apply_async(args=[order.id], countdown=30)
```

## Monitoring

In development, use the Django admin at `/admin/django_celery_beat/` to manage periodic tasks.
