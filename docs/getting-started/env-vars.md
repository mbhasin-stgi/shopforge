# Environment Variables

All environment variables are loaded from `.env` files by `docker-compose` and `django-environ`.

## Setup

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
nano .env
```

## Variables Reference

### Django

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | — | Django secret key. **Required.** Generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | `True` | Set to `False` in production |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hostnames |
| `DJANGO_ADMIN_EMAIL` | `admin@shopforge.dev` | Admin email for ADMINS setting |

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgres://shopforge:shopforge@postgres:5432/shopforge` | Full Postgres connection URL | <!-- pragma: allowlist secret -->

### Redis / Celery

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection URL |

### Email (Development)

| Variable | Default | Description |
|----------|---------|-------------|
| `EMAIL_HOST` | `mailhog` | SMTP host (MailHog in dev) |
| `EMAIL_PORT` | `1025` | SMTP port |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_DSN` | — | Sentry error tracking DSN (production only) |
| `GUNICORN_WORKERS` | `4` | Number of Gunicorn worker processes |
| `GUNICORN_THREADS` | `2` | Threads per worker |
