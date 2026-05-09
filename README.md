# 🏪 ShopForge

A corporate-grade e-commerce platform built with Django 4.2, Django REST Framework, Vue 3, and a modern DevOps pipeline.

## Quick Start

```bash
# Clone and enter the repo {#clone-and-enter-the-repo  data-source-line="603"}
git clone git@github.com:your-org/shopforge.git
cd shopforge

# Copy environment file {#copy-environment-file  data-source-line="607"}
cp .env.example .env

# Build and run {#build-and-run  data-source-line="610"}
make build
make run
``` {data-source-line="613"}

Visit: http://localhost:8000/

## Tech Stack

- **Backend:** Django 4.2 LTS, Django REST Framework, Celery
- **Frontend:** Vue 3, Vite, Vuetify, TailwindCSS
- **Database:** PostgreSQL 17
- **Cache:** Redis 6
- **Containers:** Docker Compose
- **CI/CD:** GitHub Actions

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
