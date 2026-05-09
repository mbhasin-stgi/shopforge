"""
Gunicorn configuration for production.

Usage: gunicorn -c config/gunicorn.py config.wsgi:application
All settings can be overridden via environment variables.
"""

import multiprocessing
import os

# ─── Server Socket ────────────────────────────────────────────────────
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
backlog = 2048

# ─── Worker Processes ─────────────────────────────────────────────────
# Rule of thumb: (2 × CPU cores) + 1
# More workers = more parallelism, but also more memory usage.
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = "gthread"  # Threaded workers handle DB/Redis I/O efficiently
threads = int(os.getenv("GUNICORN_THREADS", 2))
worker_connections = 1000

# ─── Worker Lifecycle ─────────────────────────────────────────────────
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))  # Kill worker if silent for 2 min
graceful_timeout = 30  # Time to finish in-flight requests on SIGTERM
keepalive = 5  # Keep idle connections open for 5s

# Restart each worker after N requests to prevent memory leaks accumulating
max_requests = 1000
# Jitter prevents all workers restarting simultaneously (thundering herd)
max_requests_jitter = 50

# ─── Temporary Directory ──────────────────────────────────────────────
# /dev/shm is a RAM-backed tmpfs — faster than disk for heartbeat files
worker_tmp_dir = "/dev/shm"  # nosec B108

# ─── Logging ──────────────────────────────────────────────────────────
accesslog = "-"  # stdout — collected by Docker/your log aggregator
errorlog = "-"  # stderr
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")

# Apache Combined Log Format + response time in microseconds (%D)
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# ─── Process Naming ───────────────────────────────────────────────────
proc_name = "shopforge"

# ─── Security ─────────────────────────────────────────────────────────
limit_request_line = 4094  # Max URL length
limit_request_fields = 100  # Max HTTP headers
limit_request_field_size = 8190  # Max header value size
