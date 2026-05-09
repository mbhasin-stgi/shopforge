# Changelog

All notable changes to ShopForge are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versions follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added
- Multi-stage production Dockerfile (~180 MB image)
- GitHub Actions CI/CD pipeline (lint, test, security, build)
- Pre-commit hooks (Black, isort, flake8, bandit, detect-secrets, ESLint, Prettier)
- Health check endpoint (`GET /api/health/`)
- Celery background tasks for order confirmation emails and inventory alerts
- Vue 3 SPA with Pinia state management and Vuetify 3 UI
- Shopping cart with quantity controls
- Order list view
- Self-hosted FontAwesome icons
- MkDocs documentation site
- CONTRIBUTING.md and CLAUDE.md

---

## [0.1.0] - 2024-01-01

### Added
- Initial project scaffold with Django 4.2 + Vue 3 + Docker Compose
- Custom User model (email-based auth, UUID primary key, role field)
- Products, Orders, Inventory, Users apps with DRF APIs
- OpenAPI schema via drf-spectacular
- Celery + Redis task queue
- PostgreSQL database
- Split Django settings (base / local / test / production)
- Makefile with developer shortcuts
