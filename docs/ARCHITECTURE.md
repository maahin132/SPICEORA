# Architecture

## Phase 0 foundation

- `frontend/`: JavaScript/JSX single-page application built with React and Vite. Tailwind CSS provides utility styling, React Router provides client-side routes, and Lucide React supplies icons.
- `backend/`: Django project with Django REST Framework. The API is namespaced under `/api/`; `/api/health/` provides a minimal liveness response.
- MySQL: local development database configured exclusively through environment variables.

The frontend and backend run as separate development servers. The frontend development server proxies `/api` requests to Django. No production hosting or product-domain model is configured in Phase 0.

## Configuration and trust boundaries

Secrets and machine-specific settings live in the untracked root `.env`. Django reads those settings at startup. CORS is restricted to configured origins. Production deployment must set `DJANGO_DEBUG=false`, define explicit allowed hosts, use TLS, and supply strong secrets through the hosting platform.
