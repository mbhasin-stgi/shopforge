# Orders API

Base URL: `/api/orders/`

Authentication required for all endpoints.

## List My Orders

```http
GET /api/orders/
Authorization: Token <token>
```

Returns orders belonging to the authenticated user. Staff see all orders.

## Get Order

```http
GET /api/orders/<order_number>/
Authorization: Token <token>
```

## Create Order

```http
POST /api/orders/
Authorization: Token <token>
Content-Type: application/json

{
  "items": [
    { "product": 1, "quantity": 2 },
    { "product": 5, "quantity": 1 }
  ],
  "shipping_address": {
    "street": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "postal_code": "62701",
    "country": "US"
  }
}
```

On success, triggers a Celery task to send an order confirmation email.

## Order Status

| Status | Meaning |
|--------|---------|
| `pending` | Created, awaiting payment |
| `paid` | Payment confirmed |
| `shipped` | Dispatched to courier |
| `delivered` | Confirmed received |
| `cancelled` | Cancelled before shipment |
| `refunded` | Payment returned |
