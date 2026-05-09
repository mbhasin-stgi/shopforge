# ============================================================
# BASE IMAGE
# ============================================================
ARG PYTHON_VERSION=3.11-slim-bullseye
FROM python:${PYTHON_VERSION} AS python-run-stage

# ============================================================
# ENVIRONMENT
# ============================================================
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    COMPOSE_PATH=./compose/local/django

# ============================================================
# WORKING DIRECTORY
# ============================================================
WORKDIR /app

# ============================================================
# SYSTEM DEPENDENCIES
# ============================================================
RUN apt-get update && apt-get install --no-install-recommends -y \
    # Python package compilation
    build-essential \
    # PostgreSQL client library (for psycopg2)
    libpq-dev \
    # File type detection
    libmagic1 \
    # Git (needed for pip packages installed from git repos)
    git \
    # Useful debugging tools
    curl \
    htop \
    net-tools \
    # PostgreSQL client (for manage.py dbshell)
    postgresql-client \
    # Cleanup
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# PYTHON DEPENDENCIES (Poetry)
# ============================================================
# Install Poetry
RUN pip install --no-cache-dir --upgrade poetry==2.1.1

# Copy dependency files first (Docker layer caching!)
COPY pyproject.toml poetry.lock /

# Install dependencies (without creating a virtualenv — we're in Docker!)
RUN poetry install --with dev --no-root --no-interaction

# ============================================================
# STARTUP SCRIPTS
# ============================================================
COPY ./compose/local/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint

COPY ${COMPOSE_PATH}/start /start
RUN sed -i 's/\r$//g' /start && chmod +x /start

COPY ${COMPOSE_PATH}/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker && chmod +x /start-celeryworker

COPY ${COMPOSE_PATH}/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat && chmod +x /start-celerybeat

# ============================================================
# ENTRYPOINT
# ============================================================
ENTRYPOINT ["/entrypoint"]
