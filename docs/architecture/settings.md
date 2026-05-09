# Settings Architecture

ShopForge uses a split settings pattern: one base file with environment-specific overrides.

## Files

| File | Used when | Key features |
|------|-----------|-------------|
| `config/settings/base.py` | Always (imported by all others) | Apps, auth, DRF, Celery, email config |
| `config/settings/local.py` | `DJANGO_SETTINGS_MODULE=config.settings.local` | DEBUG=True, MailHog, Vite dev server, CORS |
| `config/settings/test.py` | Running pytest | No socket calls, faster password hashing |
| `config/settings/production.py` | Deployed app | HTTPS, HSTS, strict CSRF, Sentry |

## Environment Variables

Settings use `django-environ` for environment variable parsing:

```python
import environ
env = environ.Env()

SECRET_KEY = env("DJANGO_SECRET_KEY")
DATABASE_URL = env.db("DATABASE_URL")
```

## How to Add a New Setting

1. Add to `base.py` with a sensible default
2. Override in `local.py` / `production.py` as needed
3. If it's a secret, use `env("VAR_NAME")` — never hardcode
