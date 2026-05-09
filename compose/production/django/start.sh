#!/bin/bash
# Production start script — launches Gunicorn.
# All settings can be overridden via environment variables.
set -euo pipefail

exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${GUNICORN_BIND_PORT:-8000}" \
    --workers "${GUNICORN_WORKERS:-4}" \
    --worker-class gthread \
    --threads "${GUNICORN_THREADS:-2}" \
    --worker-tmp-dir /dev/shm \
    --timeout "${GUNICORN_TIMEOUT:-120}" \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    --max-requests 1000 \
    --max-requests-jitter 50
