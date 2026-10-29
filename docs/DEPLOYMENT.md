# Deployment Plan

## Current state

Phase 0 configures local development only. No hosting provider, production domain, production database, CI/CD pipeline, or production topology is selected.

## Proposed launch topology

Prefer a same-origin HTTPS deployment: serve the Vite production assets through a CDN/static origin and proxy `/api/` to Django behind a production WSGI/ASGI server. Use managed MySQL on a private network where available. Select a separate frontend/API origin only if needed and configure exact CORS/CSRF trust boundaries.

## Release requirements

1. Select the hosting/data regions, domain, DNS, email delivery, media handling and support ownership.
2. Inject unique Django and database credentials via the platform secret manager; set `DEBUG=false` and explicit hosts/origins.
3. Build frontend assets with `npm run build`; do not place secrets in frontend build-time variables.
4. Run reviewed Django migrations as a controlled release step using least-privilege migration credentials.
5. Terminate TLS; configure secure cookies, trusted proxy/header behavior, HSTS and security headers for the selected infrastructure.
6. Configure encrypted automated backups, access-restricted logs, monitoring/alerts, restore drills, rollback and incident processes.
7. Verify enquiry routing, privacy notice, data retention/deletion and staff admin access before collecting personal information.

These are recommendations, not current controls. No deployment should be represented as production-ready until implemented and verified.

Phase 3 product image uploads use local Django media storage only in development (`MEDIA_ROOT`, served when `DEBUG` is enabled). Production media storage, access policy, size limits at the edge, backups, and CDN delivery are not configured. Do not enable production uploads until an approved storage and delivery design is in place.
