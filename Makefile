# ============================================================
# ShopForge — Root Makefile
# ============================================================
# This is the project-specific Makefile. It sets variables
# and includes the shared common.mk for reusable targets.
# ============================================================

# Project identity
PROJECT_NAME ?= shopforge
LOCAL_YML ?= compose/local.yml

# Default service for commands (django, celeryworker, etc.)
c ?= django

# Paths
SCRIPT_PATH ?= scripts
PATH_TO_MANAGE_PY ?= ./

# Test configuration
DIR ?= shopforge/tests/
TEST_CLASS ?=
COUNT ?= 1
TEST_SETTINGS_MODULE ?= config.settings.test

# Database
DB_USER ?= shopforge
POSTGRES_DB ?= shopforge

# Migration targets
APP_LABEL ?=
MIGRATION_NAME ?=

# Docker Compose command
DOCKER_COMPOSE ?= docker compose

# ============================================================
# Include shared targets
# ============================================================
include ${SCRIPT_PATH}/mk/common.mk

# ============================================================
# PROJECT-SPECIFIC TARGETS
# ============================================================

.PHONY: seed
seed: ## Load seed data (products, categories, etc.)
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} \
		python manage.py loaddata fixtures/seed_data.json

.PHONY: createsuperuser
createsuperuser: ## Create a superuser for admin access
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} \
		python manage.py createsuperuser

.PHONY: fresh
fresh: destroy build run ## Full reset: destroy + build + run (like first-time setup)

.PHONY: quick-start
quick-start: build ## First-time setup: build, run, migrate, seed
	@echo "🚀 Starting services..."
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env up -d
	@echo "⏳ Waiting for services to be healthy..."
	@sleep 10
	@echo "🌱 Loading seed data..."
	$(MAKE) seed
	@echo ""
	@echo "✅ ShopForge is ready!"
	@echo "   🌐 App:     http://localhost:8000/"
	@echo "   📬 MailHog: http://localhost:8025/"
	@echo "   📖 Admin:   http://localhost:8000/admin/"
	@echo ""