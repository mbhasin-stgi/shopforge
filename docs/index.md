# ShopForge Documentation

Welcome to the ShopForge technical documentation.

## What is ShopForge?

ShopForge is a production-grade e-commerce platform built with:

- **Django 4.2** — Battle-tested Python web framework (LTS)
- **Django REST Framework** — Powerful, flexible API toolkit
- **Vue 3 + Vuetify 3** — Modern reactive frontend with Material Design
- **Celery + Redis** — Background task processing (emails, inventory)
- **PostgreSQL 17** — Reliable relational database
- **Docker Compose** — Consistent dev and production environments

## Quick Links

- [Quick Start Guide](getting-started/quick-start.md)
- [API Documentation](http://localhost:8000/api/schema/swagger-ui/) *(requires running stack)*
- [Architecture Overview](architecture/overview.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## Repository Structure

```
shopforge/
├── config/          # Django settings, URLs, Celery, Gunicorn
├── shopforge/       # Application code
│   ├── apps/        # Django apps (core, users, products, orders, inventory)
│   ├── webapp/      # Vue 3 SPA (src/ → dist/)
│   ├── templates/   # Django HTML templates
│   └── static/      # Static assets (fonts, icons)
├── compose/         # Docker Compose files (local, production, pytest)
├── docs/            # This documentation site
└── .github/         # CI/CD workflows
```
