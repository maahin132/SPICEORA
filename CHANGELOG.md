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

## [Phase 2] - Homepage and visual foundation

- Replaced the Phase 0 placeholder screen with an editorial SPICEORA homepage, shared responsive navigation/header and footer, category preview, brand introduction, clearly proposed enquiry path, and an honest contact configuration placeholder.
- Added accessible mobile-menu behavior, responsive design tokens, keyboard focus styling, reduced-motion support, locally sourced and documented editorial imagery, and graceful image fallback.
- No product detail/catalogue routes, enquiry submission, backend API, database schema, dependencies, or credentials were added or changed.
- Verification results and known limitations are recorded in [PROJECT_STATUS.md](PROJECT_STATUS.md).

## [Phase 3] - Product catalogue and read API

- Added product/category models, staff admin management, image validation, and an additive migration that creates the catalogue tables and six owner-provided category labels without creating product records.
- Added anonymous read-only category/product APIs, publication filtering, validated category filtering, pagination, and product detail lookup.
- Added React catalogue/detail routes, API-driven homepage preview, and loading/empty/error/not-found states.
- Added Pillow for Django product-image validation. Production media hosting and enquiry submission remain unimplemented.
- Verification results, database target, test isolation, and remaining limitations are recorded in [PROJECT_STATUS.md](PROJECT_STATUS.md).
