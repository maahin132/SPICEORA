# SPICEORA

SPICEORA is a web application foundation with a React/Vite frontend and a Django REST backend.

## Requirements

- Node.js 20.19+ (or 22.12+) and npm
- Python 3.12
- MySQL 8.0, running locally

## Local setup

1. Copy `.env.example` to `.env` and set a unique Django secret key and local MySQL password. `.env` is ignored by Git.
2. Create and activate the backend environment, install dependencies, and prepare the database:

   ```powershell
   cd backend
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python manage.py check
   python manage.py migrate
   python manage.py check --database default
   python manage.py runserver
   ```

   The health endpoint is `http://127.0.0.1:8000/api/health/`.

3. In a separate terminal, install and run the frontend:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

   Create a production build with `npm run build`.

## Project status

See [PROJECT_STATUS.md](PROJECT_STATUS.md) for the actual bootstrap verification results and any local setup blockers. The frontend is a placeholder shell only; product pages and features are intentionally out of scope for Phase 0.
