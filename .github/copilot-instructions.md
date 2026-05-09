# Copilot Instructions for ShopForge

## Code Style

- Use double quotes for Python strings
- Use f-strings for string interpolation
- Follow PEP 8 with 120 character line length
- Use type hints for function signatures
- Add docstrings to all public functions and classes

## Django Patterns

- ViewSets for CRUD APIs (not function-based views, except simple endpoints like health check)
- Separate serializers for list vs detail views (list = fewer fields for performance)
- Custom managers for common queryset operations
- Abstract base models: `TimeStampedModel`, `UUIDModel`, `SoftDeleteModel` from `shopforge.apps.core.models`
- Always use `select_related` / `prefetch_related` in querysets to avoid N+1 queries
- Use `settings.AUTH_USER_MODEL` not a direct `User` import
- Environment variables via `django-environ` — never hardcode secrets

## Testing Patterns

- Use `@pytest.mark.django_db` for all tests that touch the database
- Use `model_bakery.baker.make()` for test fixtures — avoid manual `Model.objects.create()`
- Place shared fixtures in `conftest.py`
- Always assert the HTTP status code before asserting response data
- Mock only external services (email, payment gateway) — not internal Django/DRF code

## Frontend Patterns

- Vue 3 Composition API only — `<script setup lang="ts">` in every component
- Pinia for state management (`src/stores/`)
- All API calls via `@/services/api.ts` (axios instance with CSRF + token interceptors)
- Vuetify 3 components for all UI elements
- FontAwesome icons with `fa:fas fa-*` syntax (not mdi)
- snake_case for all API field names in TypeScript interfaces

## Security Rules

- Never log or expose SECRET_KEY, DATABASE_URL, or API tokens
- Use `@permission_classes([IsAuthenticated])` on all non-public API views
- Public endpoints must explicitly use `@permission_classes([AllowAny])`
- Never use `eval()` or `exec()` in application code
- Use `django.utils.html.escape()` when inserting user data into HTML

## Don't

- Don't use `print()` for logging — use the `logging` module
- Don't hardcode URLs — use `reverse()` or DRF's router-generated names
- Don't use `import *` except in `settings/*.py`
- Don't put business logic in views — use model methods or service functions
- Don't skip creating migrations when adding or changing model fields
- Don't commit `.env` files or any file containing real credentials
