# Products API

Base URL: `/api/products/`

## List Products

```http
GET /api/products/
```

Query parameters:
- `?search=keyword` — Full-text search on name and description
- `?category=<id>` — Filter by category
- `?is_on_sale=true` — Filter to sale items only
- `?ordering=price` — Sort by field (prefix `-` for descending)
- `?page=2&page_size=20` — Pagination

## Get Product

```http
GET /api/products/<id>/
```

## Create Product *(staff only)*

```http
POST /api/products/
Authorization: Token <token>
Content-Type: application/json

{
  "name": "Widget Pro",
  "sku": "WGT-001",
  "description": "...",
  "price": "29.99",
  "category": 1
}
```

## Update Product *(staff only)*

```http
PATCH /api/products/<id>/
Authorization: Token <token>

{ "price": "24.99" }
```

## Delete Product *(staff only)*

Products are **soft-deleted** — they are marked inactive, not removed from the database.

```http
DELETE /api/products/<id>/
Authorization: Token <token>
```

## Full API reference

See the interactive Swagger UI at `/api/schema/swagger-ui/` for all fields and response schemas.
