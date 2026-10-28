# Deployment

Phase 0 configures local development only; no hosting provider, CI/CD pipeline, or production topology is selected.

For a future deployment:

1. Provision a managed MySQL database and a dedicated least-privilege account.
2. Inject strong Django secret and database credentials using the platform's secret manager.
3. Set `DJANGO_DEBUG=false`, explicit `DJANGO_ALLOWED_HOSTS`, and production CORS origins.
4. Build the frontend with `npm run build` and serve its static assets over HTTPS.
5. Run Django migrations as a controlled release step and serve the API behind a production WSGI/ASGI server.
6. Configure TLS, backups, logging, monitoring, and restore procedures.
