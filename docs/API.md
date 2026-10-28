# API

## Base path

Backend routes are mounted at `/api/`.

## Health

`GET /api/health/` returns a minimal JSON liveness response:

```json
{"status":"ok"}
```

This endpoint indicates that Django is serving requests; it is not a database readiness probe. Keep product APIs out of scope until a later approved phase.
