# 🛒 ShopForge

A production-grade e-commerce platform built with Django 4.2, Django REST Framework, Vue 3, and Celery.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2, DRF, Celery |
| Frontend | Vue 3, Vuetify 3, TypeScript, Vite |
| Database | PostgreSQL 17 |
| Cache/Broker | Redis 6 |
| Testing | pytest, Vitest |
| CI/CD | GitHub Actions |
| Containerization | Docker, Docker Compose |

## Quick Start

```bash
# Clone the repo
git clone https://github.com/yourorg/shopforge.git
cd shopforge

# Start everything (builds containers, runs migrations, seeds data)
make quick-start

# Visit the app
open http://localhost:8000
```

### Default Users

| Email | Password | Role |
|-------|----------|------|
| admin@shopforge.dev | admin123 | Admin |
| customer@shopforge.dev | customer123 | Customer |

## Development Commands

```bash
make run          # Start all services
make stop         # Stop all services
make t            # Run backend tests
make coverage     # Run tests with coverage report
make lint         # Run all linters
make format       # Auto-format code
make mm APP_LABEL=products  # Make migrations
make m            # Apply migrations
make sp           # Django shell_plus
make bash         # Shell into Django container
npm run dev       # Frontend dev server
npm run test      # Frontend tests
npm run lint      # Frontend linting
```

## Project Structure

```
shopforge/
├── config/                 # Django settings, URLs, WSGI, Celery
│   ├── settings/
│   │   ├── base.py        # Shared settings
│   │   ├── local.py       # Development overrides
│   │   ├── test.py        # Test settings
│   │   └── production.py  # Production settings
│   ├── urls.py            # Root URL routing
│   ├── api_router.py      # API URL aggregation
│   └── celery_app.py      # Celery configuration
├── shopforge/
│   ├── apps/
│   │   ├── core/          # Shared models, permissions, utilities
│   │   ├── users/         # Authentication & user management
│   │   ├── products/      # Product catalog
│   │   ├── orders/        # Order management
│   │   └── inventory/     # Stock tracking
│   ├── webapp/            # Vue 3 frontend (SPA)
│   │   ├── src/
│   │   └── dist/          # Build output (git-ignored)
│   ├── templates/         # Django templates (SPA shells)
│   └── static/            # Static assets
├── compose/               # Docker Compose files
│   ├── local.yml          # Development stack
│   ├── production.yml     # Production stack
│   └── pytest.yml         # CI test runner
├── scripts/               # Utility scripts
├── docs/                  # Project documentation (MkDocs)
└── .github/
    └── workflows/         # CI/CD pipelines
```

## API Documentation

- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- ReDoc: http://localhost:8000/api/schema/redoc/
- OpenAPI Schema: http://localhost:8000/api/schema/

## Architecture Decisions

See [docs/architecture/](docs/architecture/) for ADRs (Architecture Decision Records).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.


## Development Commands

```bash
make run          # Start all services
make t            # Run tests
make mm           # Make migrations
make m            # Apply migrations
make sp           # Django shell_plus
make bash         # Shell into Django container
``` {data-source-line="635"}

## Documentation

```bash
make build-docs   # Build MkDocs documentation
``` {data-source-line="641"}
