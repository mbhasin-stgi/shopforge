# Docker Deployment

## Production Stack

The production stack is defined in `compose/production.yml` and uses a pre-built image from GitHub Container Registry.

### Services

| Service | Image | Port |
|---------|-------|------|
| `django` | `ghcr.io/yourorg/shopforge:<tag>` | 8000 |
| `redis` | `redis:6-alpine` | internal |
| `celery_worker` | same as django | — |
| `celery_beat` | same as django | — |

> **Note**: PostgreSQL is expected as an external managed database (AWS RDS, Supabase, etc.) in production. Set `DATABASE_URL` accordingly.

### Deploy

```bash
# Set required env vars
export DATABASE_URL="postgres://user:pass@db-host:5432/shopforge"  # pragma: allowlist secret
export REDIS_URL="redis://redis:6379/0"
export SECRET_KEY="your-long-random-secret-key"  # pragma: allowlist secret
export ALLOWED_HOSTS="shopforge.com,www.shopforge.com"
export IMAGE_TAG="v1.0.0"   # or "main" for latest

# Pull and start
docker compose -f compose/production.yml pull
docker compose -f compose/production.yml up -d
```

### Multi-Stage Dockerfile

The production Dockerfile has 3 stages:
1. **python-build-stage** — Installs Python deps into `/opt/venv`
2. **frontend-build-stage** — Builds Vue 3 assets with Vite
3. **runtime** — Slim Python image with only the venv + compiled assets

Result: ~180 MB image vs ~1.2 GB for a naive single-stage build.

## Health Check

```bash
curl http://your-server:8000/api/health/
# → {"status": "healthy", "checks": {"database": "ok", "cache": "ok"}}
```
