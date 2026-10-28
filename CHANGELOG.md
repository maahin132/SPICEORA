# Changelog

All notable project changes are recorded here.

## [0.1.0] - Phase 0

- Bootstrapped the React/Vite frontend and Django REST backend foundations.
- Added environment-based local configuration and secret/credential ignore rules.
- Added project architecture, API, database, security, testing, deployment, and roadmap documentation.
- Added GitHub issue and pull request templates.
- Frontend production build/lint and Django system check/health endpoint test passed; both frontend and Django health endpoints returned HTTP 200.
- MySQL database `spiceora_db` and local app user `spiceora_app` were created and database access was verified.
- Django migrations and database connectivity checks passed after correcting the host-specific MySQL account configuration.
- Initial commit and subsequent status updates were pushed and verified on GitHub.
- 2026-10-28 re-verification: backend test passed (1 test); MySQL rejected the updated `spiceora_app` credentials with error 1045, so migrations were not rerun. See [PROJECT_STATUS.md](PROJECT_STATUS.md).
