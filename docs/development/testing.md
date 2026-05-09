# Testing

## Backend Tests (pytest)

### Run tests

```bash
make t                                        # All tests
make t DIR=shopforge/apps/products/tests/     # Specific app
make coverage                                 # With coverage report
```

### Writing a test

```python
import pytest
from model_bakery import baker


@pytest.mark.django_db
class TestProductAPI:
    def test_list_returns_200(self, api_client):
        baker.make("products.Product", _quantity=3)
        response = api_client.get("/api/products/")
        assert response.status_code == 200
        assert len(response.data["results"]) == 3

    def test_unauthenticated_cannot_create(self, api_client):
        response = api_client.post("/api/products/", data={})
        assert response.status_code == 401
```

### Fixtures (conftest.py)

Shared fixtures live in `shopforge/tests/conftest.py`:
- `api_client` — DRF `APIClient`
- `auth_client` — Authenticated `APIClient`
- `admin_user` — Superuser instance
- `customer_user` — Regular user instance

## Frontend Tests (Vitest)

```bash
npm run test        # Watch mode
npm run test:run    # Single run
npm run coverage    # With coverage
```

Test files live alongside source files as `*.spec.ts`.

## Coverage Thresholds

- Backend: 85% minimum (enforced in CI by `coverage report --fail-under=85`)
- Frontend: reported but not enforced at this time
