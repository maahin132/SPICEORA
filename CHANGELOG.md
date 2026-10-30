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

## [Phase 4] - Export enquiry system

- Added the export enquiry model, validated public create endpoint, opaque receipt reference, IP-based submission throttle, and Django admin enquiry triage.
- Added the responsive enquiry form, loading/validation/pending/success/error states, and product-specific enquiry preselection.
- No email provider, privacy notice, retention policy, shared production rate-limit cache, or multi-product quote workflow is configured.
- Verification results and launch limitations are recorded in [PROJECT_STATUS.md](PROJECT_STATUS.md).

## [Phase 5] - Admin product management and content workflow

- Improved Django Admin product/category workflows, publication controls, product search/filter/order, timestamps, and safe image previews.
- Added matching-content/extension, file-size and dimension validation for product images, plus UUID-based filenames for new uploads.
- Protected products referenced by enquiries from deletion; existing category and enquiry records were preserved. No product content or schema columns were added.
- The reviewed migration changes Django ORM deletion behavior and image upload metadata only; generated database SQL was a no-op. Production media hosting remains unconfigured.
- Verification results and image-storage limitations are recorded in [PROJECT_STATUS.md](PROJECT_STATUS.md).

## [Phase 6] - Real product catalogue and content preparation

- Added a blank owner-editable CSV intake template for the six existing categories and documented required verified content and optional evidence-backed product details.
- Documented genuine product-photo requirements, preferred square 1600 px imagery, accepted formats, upload limits, safe naming, licensing, and alt-text guidance.
- Improved catalogue empty states with an export-enquiry path, added semantic product-detail description structure, and route-specific titles/meta descriptions using approved product name/summary only.
- No product records, product images, model fields, schema changes, or migrations were added. Existing categories and enquiry data remain unchanged.
- Verification results and owner content requirements are recorded in [PROJECT_STATUS.md](PROJECT_STATUS.md).

## [Phase 7] - Own farm and crop traceability foundation

- Added private Farm, CropSeason, Harvest, ProductionBatch, ProcessingRecord, and InventoryMovement models with protected relationships, validation, and historical-record safeguards.
- Creating a production batch atomically records its initial receipt; inventory is calculated from an immutable movement ledger with kilogram normalization, reservations, releases, dispatches, processing adjustments, and permission-gated corrections.
- Added searchable Django Admin workflows and paginated staff-only session-authenticated API collections with per-model permissions and CSRF protection. No custom React operations UI was added because the public frontend has no secure staff authentication flow.
- Applied reviewed additive migration `api.0004_farm_cropseason_harvest_productionbatch_and_more` to `spiceora_db`; no records were seeded and existing categories/products/enquiries were preserved.
- Verification results, inventory rules, security boundaries, and limitations are recorded in [PROJECT_STATUS.md](PROJECT_STATUS.md).
