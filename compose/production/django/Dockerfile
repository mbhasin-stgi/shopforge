# ══════════════════════════════════════════════════════════════════════
# Stage 1: Python Dependencies (Builder)
# ══════════════════════════════════════════════════════════════════════
# Installs all Python packages into a virtualenv.
# The virtualenv is then copied to the runtime stage — no pip/gcc ships
# to production.
FROM python:3.12-slim-bookworm AS python-build-stage

ARG BUILD_DATE
ARG VCS_REF

# System packages needed only to COMPILE Python extensions (not to run them)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Pin Poetry version — avoids "works locally, breaks in CI" surprises
RUN pip install --no-cache-dir poetry==1.7.1

WORKDIR /app

# Copy only dependency files first — Docker caches this layer and skips
# re-installing packages when only application code changes
COPY pyproject.toml poetry.lock ./

# Export to requirements.txt so we don't need Poetry at runtime
RUN poetry export -f requirements.txt --without-hashes --only=main > requirements.txt

# Build a self-contained virtualenv we can COPY to the runtime stage
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt


# ══════════════════════════════════════════════════════════════════════
# Stage 2: Frontend Build
# ══════════════════════════════════════════════════════════════════════
# Builds Vue 3 + Vite assets. The compiled dist/ folder is copied to
# the runtime stage — Node.js does NOT ship to production.
FROM node:20-alpine AS frontend-build-stage

WORKDIR /app

# Install npm deps first (cached if package files don't change)
COPY package.json package-lock.json ./
RUN npm ci --production=false

# Copy frontend source and all config files needed by vite/ts/tailwind
COPY shopforge/webapp/ shopforge/webapp/
COPY vite.config.ts tsconfig*.json tailwind.config.ts postcss.config.js env.d.ts ./

# Produce the compiled static assets in shopforge/webapp/dist/
RUN npm run build


# ══════════════════════════════════════════════════════════════════════
# Stage 3: Runtime (Final Image)
# ══════════════════════════════════════════════════════════════════════
# Slim Python image with no gcc, no pip, no Node — just our app + deps.
FROM python:3.12-slim-bookworm AS runtime

# Redeclare ARGs in this stage — Docker ARG scope is per-stage
ARG BUILD_DATE
ARG VCS_REF

# OCI-standard labels for image traceability
LABEL org.opencontainers.image.created="${BUILD_DATE}"
LABEL org.opencontainers.image.revision="${VCS_REF}"
LABEL org.opencontainers.image.title="shopforge"
LABEL org.opencontainers.image.description="ShopForge Django Application"

# Minimal runtime deps:
# - libpq5: PostgreSQL client library (psycopg2 needs this at runtime)
# - curl: used by the Docker HEALTHCHECK command
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove

# SECURITY: never run as root in production
# -r = system account (no login shell, no home dir creation)
RUN groupadd -r shopforge && useradd -r -g shopforge -d /app -s /sbin/nologin shopforge

# Pull the virtualenv from Stage 1 (no pip install needed here)
COPY --from=python-build-stage /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Pull the compiled Vue/Vite assets from Stage 2
COPY --from=frontend-build-stage /app/shopforge/webapp/dist /app/shopforge/webapp/dist

WORKDIR /app

# Copy application source code
# .dockerignore excludes .git, node_modules, .env files, etc.
COPY . .

# Collect static files (Django admin CSS, self-hosted fonts, Vite assets)
# The || true prevents build failure if production settings need DB (they shouldn't for collectstatic)
RUN DJANGO_SETTINGS_MODULE=config.settings.production \
    SECRET_KEY=collectstatic-placeholder-not-used-at-runtime \
    DATABASE_URL=sqlite:///tmp/collectstatic.db \
    python manage.py collectstatic --noinput 2>/dev/null || true

# Pre-compile Python to .pyc bytecode — saves ~100ms per module on first import
RUN python -m compileall -q shopforge/ config/

# Strip files that should never be in a production image
RUN rm -rf \
    .git \
    .github \
    compose/local/ \
    node_modules/ \
    shopforge/webapp/src/ \
    Makefile

# Give the non-root user ownership of the app directory
RUN chown -R shopforge:shopforge /app

# Make entrypoint and start scripts executable
RUN chmod +x compose/production/django/entrypoint.sh \
             compose/production/django/start.sh

USER shopforge

EXPOSE 8000

# Docker checks this every 30s. If it fails 3 times, the container is
# marked unhealthy and the orchestrator can replace it.
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

ENTRYPOINT ["/app/compose/production/django/entrypoint.sh"]
CMD ["/app/compose/production/django/start.sh"]
