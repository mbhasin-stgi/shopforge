# ADR-001: Custom User Model

## Status: Accepted

## Date: 2024-01-01

## Context

Django's built-in `auth.User` model uses `username` as the primary login identifier. ShopForge requires:
- Email-based authentication (no username)
- Role-based access control (Customer, Staff, Vendor, Admin)
- UUID primary key for security and URL obfuscation
- `created_at` / `updated_at` audit timestamps on all user records

Changing the user model after the first migration is extremely painful in Django — it requires resetting the entire database and recreating all foreign keys. This decision **must** be made before `python manage.py migrate` is run for the first time.

## Decision

Create a custom `User` model in `shopforge/apps/users/models.py` that:
- Extends `AbstractBaseUser` and `PermissionsMixin`
- Uses `email` as `USERNAME_FIELD`
- Has a `role` field with choices: `customer`, `staff`, `vendor`, `admin`
- Has a UUID `id` field as primary key
- Inherits `created_at` / `updated_at` from `TimeStampedModel`

Set `AUTH_USER_MODEL = "users.User"` in `config/settings/base.py`.

## Consequences

**Positive:**
- Email-based login is natural for e-commerce
- UUID PKs prevent enumeration attacks on user IDs
- Role field enables RBAC without needing complex group setup
- Audit timestamps on all users for free

**Negative:**
- Third-party packages that hardcode `from django.contrib.auth.models import User` may need patching
- All FKs to User must use `settings.AUTH_USER_MODEL`, never a direct import

## Compliance

All code in this codebase **must** reference the user model as:
```python
from django.conf import settings
# In model field:
user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
# In code:
from django.contrib.auth import get_user_model
User = get_user_model()
```
