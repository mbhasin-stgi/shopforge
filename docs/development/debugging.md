# Debugging

## Django Backend

### Django Debug Toolbar

Available at `http://localhost:8000/__debug__/` in development. Shows SQL queries, cache hits, template context.

### shell_plus

Drop into a Django shell with all models auto-imported:

```bash
make sp
# then:
>>> Product.objects.filter(is_active=True).count()
>>> Order.objects.select_related("user").last()
```

### Django container logs

```bash
make logs           # All services
make logs-django    # Django only
```

### Celery tasks

```bash
make logs-celery    # Celery worker logs
```

## Frontend

### Vite HMR

The Vite dev server runs on `http://localhost:5174` and provides Hot Module Replacement — changes to `.vue` files reload instantly without a full page refresh.

### Vue DevTools

Install the [Vue DevTools browser extension](https://devtools.vuejs.org/) to inspect component state, Pinia stores, and the router.

### API errors

All API errors are surfaced in the browser console and via the `useNotification` composable which shows a snackbar.

## Common Issues

| Issue | Likely cause | Fix |
|-------|-------------|-----|
| CSRF 403 on POST | Cookie not set | Visit any page first to get the cookie, then POST |
| Icons showing as squares | FontAwesome not loaded | Check `{% static 'fontawesome/css/all.min.css' %}` loads in Network tab |
| Celery task not running | Redis not started | `make run` to ensure all services are up |
| DB connection refused | Postgres not ready | Wait a few seconds and retry; check `make logs-postgres` |
