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
- 2026-10-28: Diagnosed MySQL 1045 as different credentials for the `localhost` and `127.0.0.1` app accounts. Updated only ignored local `.env` to use `DB_HOST=localhost`; Django connection checks passed, migrations were current, and backend tests passed (1 test). No database, account, password, or grant was changed. See [PROJECT_STATUS.md](PROJECT_STATUS.md).

## [Phase 1] - Requirements and architecture

- Documented business goals, non-goals, buyer journeys, product-content safeguards and owner-confirmation questions.
- Defined the proposed sitemap, launch/deferred pages, page sections, CTAs, data needs and mobile behavior.
- Expanded the application, database, API, security, testing and deployment plans without implementing features or changing the schema.
- Added an original editorial visual brief using the owner-provided palette.
- No frontend/backend implementation, dependencies, database contents, or credentials were changed.
