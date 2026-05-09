# CLAUDE.md

This file provides guidance to AI coding assistants (Claude, Copilot, etc.) working with this repository.

## Repository Overview

ShopForge is a Django 4.2 + Vue 3 e-commerce platform running in Docker Compose.
The Django backend serves a REST API; the Vue 3 SPA is the frontend, served via Vite in dev
and as compiled static assets in production.

## Common Commands

### Run / Build
- `make run` — Start all services (Django + Celery + Postgres + Redis + Vite)
- `make build` — Build Docker containers
- `make quick-start` — First-time setup (build + migrate + seed + run)
- `make stop` — Stop all containers

### Tests
- `make t` — Run pytest (all tests)
- `make t DIR=shopforge/apps/products/tests/` — Run specific tests
- `make coverage` — Tests with coverage report
- `npm run test` — Frontend tests (Vitest)
- `npm run coverage` — Frontend tests with coverage

### Code Quality
- `make lint` — Run all linters (pre-commit run --all-files)
- `make format` — Auto-format (Black + isort + Prettier)
- `pre-commit run --all-files` — Run all pre-commit hooks manually

### Database
- `make mm APP_LABEL=<app>` — Create migrations for an app
- `make m` — Apply all pending migrations
- `make sp` — Django shell_plus (auto-imports all models)
- `make bash` — Shell into the running Django container

### Documentation
- `make serve-docs` — Serve MkDocs site on port 8001

## Architecture

- **Settings**: `config/settings/{base,local,test,production}.py`
  - `base.py` — shared across all environments
  - `local.py` — dev overrides (DEBUG=True, MailHog SMTP, Vite dev server)
  - `test.py` — test overrides (SQLite optional, no socket calls)
  - `production.py` — production hardening (HTTPS, HSTS, etc.)
- **URLs**: `config/urls.py` → `config/api_router.py` → per-app `api/urls.py`
- **Models**: Use abstract bases from `shopforge.apps.core.models`
- **APIs**: DRF ViewSets with separate list/detail serializers
- **Tasks**: Celery tasks in each app's `tasks.py`, routed by queue
- **Frontend**: Vue 3 SPA in `shopforge/webapp/src/`
  - Pinia stores: `src/stores/auth.ts`, `src/stores/cart.ts`
  - API service: `src/services/api.ts` (axios, CSRF-aware)
  - Router: `src/router/index.ts` (eager imports for main routes)

## Conventions

- **Python**: Black (120 cols), isort (black profile), double quotes, f-strings
- **Frontend**: ESLint + Prettier, Composition API with `<script setup lang="ts">`, TypeScript strict
- **Tests**: pytest + model-bakery (backend), Vitest (frontend)
- **Commits**: Conventional Commits — `feat/fix/docs/refactor/test/ci/chore`
- **Branches**: `feature/*`, `bugfix/*`, `hotfix/*` → PR to `develop` → merge to `main`
- **API fields**: snake_case in both Django serializers and Vue TypeScript interfaces

## Key Decisions

- Custom User model with email-based auth (no username)
- UUID primary keys on all customer-facing models
- Soft-delete on products (never lose historical data)
- Separate list/detail serializers for performance
- Task routing by queue: `emails`, `inventory`, `default`
- Multi-stage Docker builds (~180 MB production image)
- Self-hosted FontAwesome (no CDN — avoids SRI hash issues)
- CSRF_COOKIE_HTTPONLY=False so Vue/axios can read the cookie

## Important File Locations

- Django entry: `manage.py` (run from `shopforge/` directory)
- Celery app: `config/celery_app.py`
- Vue entry: `shopforge/webapp/src/main.ts`
- Vite config: `vite.config.ts`
- Docker dev: `compose/local.yml`
- Docker prod: `compose/production.yml`
- Health check: `GET /api/health/`
