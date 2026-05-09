# Monitoring

## Health Check Endpoint

```
GET /api/health/
```

Returns:
```json
{
  "status": "healthy",
  "checks": {
    "database": "ok",
    "cache": "ok"
  }
}
```

- `200 OK` — all systems healthy
- `503 Service Unavailable` — one or more checks failed

Use this URL with your load balancer, uptime monitor (Better Uptime, UptimeRobot), or Kubernetes liveness probe.

## Logging

All services log to stdout/stderr in JSON-friendly format, collected by Docker's log driver.

```bash
# View logs
docker compose -f compose/production.yml logs -f django
docker compose -f compose/production.yml logs -f celery_worker
```

## Error Tracking (Sentry)

Set `SENTRY_DSN` in your environment. Django will automatically capture:
- Unhandled exceptions
- Slow requests (performance traces)
- Celery task failures

## Metrics

For production metrics, consider adding:
- **Prometheus** — Django metrics via `django-prometheus`
- **Grafana** — Dashboard for request rates, error rates, DB query times
- **Celery Flower** — Web UI for monitoring Celery workers and task queues
