# Developer Quickstart

## Prerequisites

- Windows 10/11
- Python 3.12 or a compatible supported Python 3 version
- Node.js and npm compatible with the Vite application
- Git
- MySQL 8 only when testing or developing against the local application database

Verify tools with:

```powershell
python --version
node --version
npm --version
git --version
```

## Repository setup

```powershell
cd D:\SPICEORA
git status
git switch main
git pull --ff-only origin main
```

Do not use destructive Git commands to recover local documentation changes.

## Isolated backend setup

No application database or `.env` value is required for the documented in-memory SQLite test configuration. From the repository root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py test --settings=config.test_settings
```

Deactivate the environment with:

```powershell
deactivate
```

## Local MySQL development setup

MySQL setup requires the existing owner-authorized local account and must not modify users, passwords, grants, unrelated databases, or database data as part of documentation work.

At repository root, copy the example environment only if `.env` does not already exist:

```powershell
Copy-Item .env.example .env
```

Set environment values in `.env` rather than source files:

- `DJANGO_SECRET_KEY`
- `DB_HOST`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- Optional approved Gmail SMTP values

Never print, paste, or commit `.env`. The file is ignored. Do not run commands that print environment variables or open secrets.

Start the backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python manage.py check
python manage.py migrate --check
python manage.py runserver 127.0.0.1:8000
```

A migration command is a database operation. Documentation work does not require or authorize `migrate`; apply migrations only after separately reviewed implementation approval.

## Frontend setup

From the repository root in another terminal:

```powershell
cd frontend
npm install
npm run dev
npm run test:run
npm run lint
npm run build
```

The Vite development server generally uses port 5173. It proxies `/api` and `/media` requests to Django at the configured backend origin for development.

## API proxy behavior

The frontend defaults to `/api/v1` when `VITE_API_BASE_URL` is not supplied. In development, Vite proxies API and media paths to Django. Authentication requests use session cookies and `X-CSRFToken` for unsafe methods; do not replace this session flow with JWT or localStorage token storage.

## Common checks

From `backend/`:

```powershell
python manage.py check
python manage.py check --database default
python manage.py migrate --check
python manage.py test --settings=config.test_settings
```

From `frontend/`:

```powershell
npm run test:run
npm run lint
npm run build
```

## Troubleshooting

### Django cannot connect to MySQL

- Verify MySQL is running locally.
- Verify `DB_HOST` and account authentication settings.
- Do not change passwords, grants, or users without owner authorization.
- Use localhost when the local account and authentication plugin require it.
- Do not inspect or execute `mysql_reset.sql`.

### Missing secret-key startup error

- Copy `.env.example` only if a local `.env` is not already configured.
- Set a unique non-placeholder `DJANGO_SECRET_KEY`.
- Never commit the generated value.

### Frontend API returns 401 or 403

- Confirm the browser is logged into the correct customer or staff endpoint.
- Confirm the staff user has the route's required model permission.
- Confirm CSRF initialization and `X-CSRFToken` for unsafe requests.
- Remember that frontend route/button guards are not authoritative authorization.

### Frontend API is unreachable

- Confirm Django runs on port 8000.
- Confirm Vite is running and proxy settings match the backend origin.
- Confirm browser-network requests do not expose secrets or credentials.

## Documentation-only work

Documentation batches must not:

- Modify application source or configuration
- Apply migrations
- Reset or flush databases
- Open or execute `mysql_reset.sql`
- Print `.env`
- Install dependencies unless separately approved
- Stage, commit, push, or deploy
