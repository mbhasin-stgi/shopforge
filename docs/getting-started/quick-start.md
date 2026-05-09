# Quick Start

Get ShopForge running locally in under 5 minutes.

## Prerequisites

- Docker Desktop (or Docker Engine + Compose plugin)
- `make` (pre-installed on macOS/Linux; Windows: use WSL2)
- Node.js 20+ (for frontend dev only)
- Python 3.11+ with Poetry (for running hooks locally)

## Steps

### 1. Clone the repository

```bash
git clone https://github.com/yourorg/shopforge.git
cd shopforge
```

### 2. Start everything

```bash
make quick-start
```

This command:
1. Builds all Docker images
2. Starts Postgres, Redis, Django, Celery, Vite
3. Applies database migrations
4. Seeds initial data (admin user, sample products)

### 3. Open the app

| URL | What |
|-----|------|
| http://localhost:8000 | Main application |
| http://localhost:8000/admin/ | Django admin |
| http://localhost:8000/api/schema/swagger-ui/ | API docs |
| http://localhost:8025 | MailHog (dev email viewer) |
| http://localhost:5174 | Vite HMR dev server |

### Default credentials

| Email | Password | Role |
|-------|----------|------|
| admin@shopforge.dev | admin123 | Admin |
| customer@shopforge.dev | customer123 | Customer |

## Stopping

```bash
make stop
```
