#!/bin/bash
# Production entrypoint — runs before Gunicorn starts.
# Responsibilities:
#   1. Wait until PostgreSQL is accepting connections
#   2. Apply any pending database migrations
#   3. Hand off to the main command (start.sh → gunicorn)
set -euo pipefail

# ─── Wait for PostgreSQL ──────────────────────────────────────────────
# psycopg2 accepts a URL directly as the DSN argument.
echo "Waiting for PostgreSQL..."
until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(os.environ['DATABASE_URL'])
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; do
    echo "  PostgreSQL not ready — retrying in 1s..."
    sleep 1
done
echo "PostgreSQL is ready!"

# ─── Apply migrations ─────────────────────────────────────────────────
echo "Applying database migrations..."
python manage.py migrate --noinput

# ─── Hand off to the main process ─────────────────────────────────────
# exec replaces this shell with the target process so signals (SIGTERM etc.)
# go directly to Gunicorn, enabling graceful shutdown.
exec "$@"
