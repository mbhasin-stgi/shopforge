# Architecture Overview

## System Components

```
┌─────────────────────────────────────────────────────────┐
│                     Browser / Client                     │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP
┌─────────────────────▼───────────────────────────────────┐
│              Django (Gunicorn, port 8000)                │
│                                                          │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────┐  │
│  │  Vue 3 SPA   │   │  REST API    │   │ Django Admin│  │
│  │  (AppView)   │   │  (DRF)       │   │  /admin/    │  │
│  └──────────────┘   └──────┬───────┘   └─────────────┘  │
└─────────────────────────────┼───────────────────────────┘
                              │
         ┌────────────────────┼──────────────────┐
         │                    │                  │
┌────────▼───────┐   ┌───────▼──────┐  ┌────────▼───────┐
│   PostgreSQL   │   │    Redis     │  │  Celery Worker  │
│   (Database)   │   │ (Cache +     │  │  (Background    │
│                │   │  Broker)     │  │   Tasks)        │
└────────────────┘   └──────────────┘  └────────────────┘
```

## Request Flow

1. Browser hits `http://localhost:8000`
2. Django's URL router checks: does this match an API or admin route?
3. **No** → `AppView` returns the SPA HTML shell (Vue takes over)
4. **Yes** → DRF ViewSet handles the request, returns JSON

## App Structure

Each Django app follows this layout:
```
shopforge/apps/<app>/
├── models.py        # Data models
├── admin.py         # Admin registration
├── tasks.py         # Celery background tasks
├── api/
│   ├── serializers.py  # DRF serializers
│   ├── views.py        # DRF ViewSets
│   ├── urls.py         # URL patterns
│   └── permissions.py  # Custom permissions
└── tests/
    └── test_*.py
```
