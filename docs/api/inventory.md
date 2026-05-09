# Inventory API

Base URL: `/api/inventory/`

Staff/admin access required for write operations.

## List Stock Levels

```http
GET /api/inventory/
Authorization: Token <token>
```

## Get Stock for Product

```http
GET /api/inventory/<product_id>/
Authorization: Token <token>
```

Response:
```json
{
  "product": 1,
  "product_name": "Widget Pro",
  "quantity_on_hand": 142,
  "low_stock_threshold": 10,
  "is_low_stock": false
}
```

## Update Stock *(staff only)*

```http
PATCH /api/inventory/<product_id>/
Authorization: Token <token>

{ "quantity_on_hand": 200 }
```

When stock drops below `low_stock_threshold`, a Celery task fires a low-stock alert email to the configured admin address.
