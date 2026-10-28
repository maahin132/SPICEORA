# Testing

## Backend

From `backend/` with the virtual environment active:

```powershell
python manage.py check
python manage.py check --database default
python manage.py migrate --check
python manage.py test
```

The database check requires a running MySQL server and valid `.env` credentials.

## Frontend

From `frontend/`:

```powershell
npm run build
```

The production build validates compilation and asset bundling. Record actual Phase 0 command results in [PROJECT_STATUS.md](../PROJECT_STATUS.md).
