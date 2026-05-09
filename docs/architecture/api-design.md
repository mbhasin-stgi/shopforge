# API Design

## URL Structure

All API routes are under `/api/` and registered in `config/api_router.py`:

```
/api/health/                  → Health check (GET, no auth)
/api/products/                → Product catalog
/api/orders/                  → Order management
/api/users/                   → User management
/api/inventory/               → Stock tracking
/api/auth/                    → dj-rest-auth (login, logout, register)
/api/schema/                  → OpenAPI 3 schema (YAML)
/api/schema/swagger-ui/       → Swagger UI
/api/schema/redoc/            → ReDoc
```

## Authentication

Token authentication via `dj-rest-auth`:

```bash
# Login
POST /api/auth/login/
{ "email": "user@example.com", "password": "..." }
→ { "key": "<token>" }

# Use token in subsequent requests
Authorization: Token <token>
```

## Serializer Convention

Use separate serializers for list and detail views:

```python
class ProductListSerializer(serializers.ModelSerializer):
    """Minimal fields for list performance."""
    class Meta:
        fields = ["id", "name", "price", "primary_image"]

class ProductDetailSerializer(serializers.ModelSerializer):
    """Full fields for single-object views."""
    class Meta:
        fields = "__all__"
```

## Pagination

Default pagination is 20 items per page. Override with `?page_size=N` (max 100).
