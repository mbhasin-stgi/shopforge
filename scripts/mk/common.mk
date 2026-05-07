# ============================================================
# common.mk — Shared Make targets for Django + Docker projects
# ============================================================
# This file is included by the project's root Makefile.
# Variables like PROJECT_NAME, LOCAL_YML, etc. should be set before including.

# ============================================================
# HELP
# ============================================================
.PHONY: help
help: ## Show available commands
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":[^:]*## "}; {split($$1, a, ":"); printf "  \033[36m%-20s\033[0m %s\n", a[2], $$2}'
	@echo ""

# ============================================================
# DOCKER LIFECYCLE
# ============================================================
.PHONY: build
build: stop ## Build all containers
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env build --pull

.PHONY: run
run: ## Start all services
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env up --remove-orphans

.PHONY: run-lite
run-lite: ## Start services (skip init scripts for faster restart)
	SKIP_INIT_LOCAL=1 ${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env up --remove-orphans

.PHONY: stop
stop: ## Stop all running containers
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env stop

.PHONY: restart
restart: ## Restart a service (default: django). Usage: make restart c=celeryworker
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env restart ${c}

.PHONY: destroy
destroy: ## Destroy all containers and volumes
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env rm -svf
	docker volume prune -f

.PHONY: rebuild
rebuild: destroy build ## Destroy, rebuild, ready to run — shortcut: r

r: rebuild

.PHONY: armageddon
armageddon: ## ☢️  Nuclear option: destroy EVERYTHING (containers, volumes, images)
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env stop
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env down -v --rmi all
	docker volume prune -f

.PHONY: lazarus
lazarus: armageddon build run ## Rise from the ashes (destroy + build + run)

# ============================================================
# DJANGO MANAGEMENT
# ============================================================
.PHONY: python-makemigrations
python-makemigrations: ## Create new migrations — shortcut: mm
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} \
		python manage.py makemigrations ${APP_LABEL} --skip-checks
mm: python-makemigrations

.PHONY: python-migrate
python-migrate: ## Apply migrations — shortcut: m
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} \
		python manage.py migrate ${APP_LABEL} ${MIGRATION_NAME}
m: python-migrate

.PHONY: python-migrations-check
python-migrations-check: ## Check for unapplied migrations — shortcut: mc
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} \
		python manage.py migrate --check
mc: python-migrations-check

.PHONY: python-migrations-plan
python-migrations-plan: ## Show migration plan — shortcut: mp
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} \
		python manage.py showmigrations ${APP_LABEL}
mp: python-migrations-plan

.PHONY: show-migrations
show-migrations: ## Show all migrations and their status — shortcut: sm
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} \
		python manage.py showmigrations
sm: show-migrations

# ============================================================
# SHELL ACCESS
# ============================================================
.PHONY: bash
bash: ## Open a bash shell in the Django container — shortcut: b
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} bash
b: bash

.PHONY: shell_plus
shell_plus: ## Open Django shell_plus (enhanced REPL) — shortcut: sp
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} \
		python manage.py shell_plus
sp: shell_plus

.PHONY: python-db-shell
python-db-shell: ## Open PostgreSQL shell — shortcut: db
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} \
		python manage.py dbshell
db: python-db-shell

.PHONY: manage
manage: ## Run any manage.py command. Usage: make manage cmd="createsuperuser"
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} \
		python manage.py ${cmd}

# ============================================================
# TESTING
# ============================================================
.PHONY: python-test
python-test: ## Run pytest — shortcut: t. Usage: make t DIR=shopforge/tests/orders/
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} /bin/bash -c '\
		export DJANGO_SETTINGS_MODULE=${TEST_SETTINGS_MODULE} && \
		unset SENTRY_DSN && \
		python -m pytest ${DIR} $(if ${TEST_CLASS},-k ${TEST_CLASS}) --count=${COUNT}'
t: python-test

.PHONY: python-test-debug
python-test-debug: ## Run pytest with debugpy attached — shortcut: td
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run -p 2282:5678 --rm ${c} /bin/bash -c '\
		export DJANGO_SETTINGS_MODULE=${TEST_SETTINGS_MODULE} && \
		unset SENTRY_DSN && \
		python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m pytest ${DIR} \
		$(if ${TEST_CLASS},-k ${TEST_CLASS}) --count=${COUNT}'
td: python-test-debug

.PHONY: coverage
coverage: ## Run tests with coverage report
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} /bin/bash -c '\
		export DJANGO_SETTINGS_MODULE=${TEST_SETTINGS_MODULE} && \
		unset SENTRY_DSN && \
		coverage run -m pytest ${DIR} && \
		coverage report && \
		coverage html'

# ============================================================
# CODE QUALITY
# ============================================================
.PHONY: lint
lint: ## Run all linters (black check + isort check + flake8)
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} /bin/bash -c '\
		echo "🖤 Running Black (check mode)..." && black --check . && \
		echo "📦 Running isort (check mode)..." && isort --check-only . && \
		echo "🔍 Running Flake8..." && flake8 .'

.PHONY: format
format: ## Auto-format code (black + isort)
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} /bin/bash -c '\
		echo "🖤 Running Black..." && black . && \
		echo "📦 Running isort..." && isort .'

.PHONY: pylint
pylint: ## Run Pylint
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} \
		pylint shopforge/ --load-plugins pylint_django --django-settings-module=config.settings.local

# ============================================================
# DATABASE UTILITIES
# ============================================================
.PHONY: db-backup
db-backup: stop ## Backup the local database
	docker run --rm -v shopforge_postgres_data:/data -v $(PWD)/backups:/backup \
		alpine tar czf /backup/db_backup_$$(date +%Y%m%d_%H%M%S).tar.gz /data

.PHONY: db-delete-test
db-delete-test: ## Drop the test database
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env exec postgres \
		psql -U ${DB_USER} -d postgres -c "DROP DATABASE IF EXISTS test_${POSTGRES_DB};"

# ============================================================
# REDIS
# ============================================================
.PHONY: redis-cli
redis-cli: ## Open Redis CLI
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm redis redis-cli -h redis

# ============================================================
# FRONTEND
# ============================================================
.PHONY: vitest
vitest: ## Run frontend unit tests
	npm run test

.PHONY: npm-build
npm-build: ## Build frontend for production
	npm run build

# ============================================================
# DOCUMENTATION
# ============================================================
.PHONY: build-docs
build-docs: ## Build MkDocs documentation
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} \
		mkdocs build --clean

.PHONY: serve-docs
serve-docs: ## Serve docs locally on port 8002
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run -p 8002:8000 --rm ${c} \
		mkdocs serve --dev-addr 0.0.0.0:8000

# ============================================================
# OPENAPI SCHEMA
# ============================================================
.PHONY: schema
schema: ## Generate OpenAPI schema
	${DOCKER_COMPOSE} -f ${LOCAL_YML} -p ${PROJECT_NAME} --env-file=./.env run --rm ${c} \
		python manage.py spectacular --color --file schema.json