# Deployment Plan

## Current state

Phase 0 configures local development only. No hosting provider, production domain, production database, CI/CD pipeline, or production topology is selected.

## Proposed launch topology

Prefer a same-origin HTTPS deployment: serve the Vite production assets through a CDN/static origin and proxy `/api/` to Django behind a production WSGI/ASGI server. Use managed MySQL on a private network where available. Select a separate frontend/API origin only if needed and configure exact CORS/CSRF trust boundaries.

## Release requirements

1. Select the hosting/data regions, domain, DNS, email delivery, media handling and support ownership. SMS is deferred.
2. Inject a unique Django `DJANGO_SECRET_KEY` and database credentials via the platform secret manager; startup rejects a missing/empty or example-placeholder secret key. Set `DEBUG=false` and explicit hosts/origins.
3. Build frontend assets with `npm run build`; do not place secrets in frontend build-time variables.
4. Run reviewed Django migrations as a controlled release step using least-privilege migration credentials.
5. Terminate TLS; configure secure cookies, trusted proxy/header behavior, HSTS and security headers for the selected infrastructure.
6. Configure encrypted automated backups, access-restricted logs, monitoring/alerts, restore drills, rollback and incident processes.
7. Verify enquiry routing, privacy notice, data retention/deletion and staff admin access before collecting personal information.
8. For low-volume testing only, configure personal Gmail SMTP: use an eligible personal Google account, enable 2-Step Verification, create a Google App Password, and set `EMAIL_PROVIDER=gmail`, `GOOGLE_SMTP_HOST=smtp.gmail.com`, `GOOGLE_SMTP_PORT=587`, `GOOGLE_SMTP_LOGIN` (full Gmail address), `GOOGLE_SMTP_APP_PASSWORD` (App Password, not the normal Google password), and matching `DEFAULT_FROM_EMAIL` in the secret store. Do not use a paid Google Workspace account for this no-cost configuration. The application enforces TLS on port 587 and refuses other SMTP providers. Follow Google's [App Password guidance](https://support.google.com/accounts/answer/185833?hl=en); App Passwords require 2-Step Verification and may not be available for managed/protected accounts.
9. Treat personal Gmail SMTP as a low-volume development/test option only. Google may apply account sending limits, spam controls, or block suspicious sending; OTP delivery is not guaranteed for production. No exact quota is assumed by the application. A controlled test to the owner-approved inbox confirmed receipt for both registration-style and forgot-password OTP emails; this is not a production delivery guarantee. Mobile verification and SMS recovery remain disabled; no SMS provider credentials or SMS testing are permitted in this phase.
10. Set exact `DJANGO_CORS_ALLOWED_ORIGINS` and `DJANGO_CSRF_TRUSTED_ORIGINS`; configure `DJANGO_SECURE_COOKIES=true` and review session/CSRF `SameSite` settings for the final origin topology. Use `SameSite=None` only for an approved cross-site HTTPS design.
11. Configure a shared production cache and review account/IP throttle rates. The development local-memory throttle does not coordinate across application workers.

These are recommendations, not current controls. No deployment should be represented as production-ready until implemented and verified.

Phase 3 product image uploads use local Django media storage only in development (`MEDIA_ROOT`, served when `DEBUG` is enabled). Production media storage, access policy, size limits at the edge, backups, and CDN delivery are not configured. Do not enable production uploads until an approved storage and delivery design is in place.
