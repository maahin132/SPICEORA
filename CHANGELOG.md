# Changelog

All notable project changes are recorded here.

## [Phase 13] - Documentation overhaul (unreleased)

- Added the documentation hub, authentication guide, workflow guide, developer quickstart, and owner-confirmation checklist.
- Updated architecture and database documentation with verified system and entity relationship Mermaid diagrams.
- Reconciled the API reference, testing guide, roadmap, information architecture, and security boundaries to source-verified implementation behavior.
- Added source-verified Phase 12 release and test evidence without changing application code, migrations, database state, dependencies, staging state, or Git history.
- Documentation-only implementation remains unstaged and uncommitted pending separate release approval.

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
- Released under commit `9795af283f332a41e2dbb863e06c6ff54bf98466`.

## [Phase 2] - Homepage and visual foundation

- Replaced the Phase 0 placeholder screen with an editorial SPICEORA homepage, shared responsive navigation/header and footer, category preview, brand introduction, clearly proposed enquiry path, and an honest contact configuration placeholder.
- Added accessible mobile-menu behavior, responsive design tokens, keyboard focus styling, reduced-motion support, locally sourced and documented editorial imagery, and graceful image fallback.
- No product detail/catalogue routes, enquiry submission, backend API, database schema, dependencies, or credentials were added or changed.
- Released under commit `18b833c81e5e8b81dd92d92c25ef88e02ccf6484`.

## [Phase 3] - Product catalogue and read API

- Added product/category models, staff admin management, image validation, and an additive migration that creates the catalogue tables and six owner-provided category labels without creating product records.
- Added anonymous read-only category/product APIs, publication filtering, validated category filtering, pagination, and product detail lookup.
- Added React catalogue/detail routes, API-driven homepage preview, and loading/empty/error/not-found states.
- Added Pillow for Django product-image validation. Production media hosting and enquiry submission remain unimplemented.
- Released under commit `63020e62f0f5b50e7f59c54e22111dc835be80f7`.

## [Phase 4] - Export enquiry system

- Added the export enquiry model, validated public create endpoint, opaque receipt reference, IP-based submission throttle, and Django admin enquiry triage.
- Added the responsive enquiry form, loading/validation/pending/success/error states, and product-specific enquiry preselection.
- No email provider, privacy notice, retention policy, shared production rate-limit cache, or multi-product quote workflow is configured.
- Released under commit `827a0077a3539b1cc0631a0eb8cd25e2c111748e`.

## [Phase 5] - Admin product management and content workflow

- Improved Django Admin product/category workflows, publication controls, product search/filter/order, timestamps, and safe image previews.
- Added matching-content/extension, file-size and dimension validation for product images, plus UUID-based filenames for new uploads.
- Protected products referenced by enquiries from deletion; existing category and enquiry records were preserved. No product content or schema columns were added.
- The reviewed migration changes Django ORM deletion behavior and image upload metadata only; generated database SQL was a no-op. Production media hosting remains unconfigured.
- Released under commit `3e32230aa65a7c9d5bc59f0e37cb86aa6330b9b1`.

## [Phase 6] - Real product catalogue and content preparation

- Added a blank owner-editable CSV intake template for the six existing categories and documented required verified content and optional evidence-backed product details.
- Documented genuine product-photo requirements, preferred square 1600 px imagery, accepted formats, upload limits, safe naming, licensing, and alt-text guidance.
- Improved catalogue empty states with an export-enquiry path, added semantic product-detail description structure, and route-specific titles/meta descriptions using approved product name/summary only.
- No product records, product images, model fields, schema changes, or migrations were added. Existing categories and enquiry data remain unchanged.
- Released under commit `41f95f3b1bcff50fad57cdb3ed882daffaa555bd`.

## [Phase 7] - Own farm and crop traceability foundation

- Added private Farm, CropSeason, Harvest, ProductionBatch, ProcessingRecord, and InventoryMovement models with protected relationships, validation, and historical-record safeguards.
- Creating a production batch atomically records its initial receipt; inventory is calculated from an immutable movement ledger with kilogram normalization, reservations, releases, dispatches, processing adjustments, and permission-gated corrections.
- Added searchable Django Admin workflows and paginated staff-only session-authenticated API collections with per-model permissions and CSRF protection.
- Applied reviewed additive migration `api.0004_farm_cropseason_harvest_productionbatch_and_more` to `spiceora_db`; no records were seeded and existing categories/products/enquiries were preserved.
- Released under commit `5ee678606c8cda1700bd423dd131981450b22c72`.

## [Phase 8] - Authentication and operations dashboard

- Added customer profile and OTP challenge models without replacing Django's existing auth user model; applied additive migration `api.0005_customer_account_otp` to `spiceora_db`.
- Updated registration to activate customers after email OTP only. Mobile numbers are collected and validated in E.164 format but remain unverified; mobile login, SMS verification and SMS recovery are disabled.
- Restricted email to personal Gmail SMTP (`smtp.gmail.com:587` with TLS) via Google App Password for low-volume testing only. Missing credentials or delivery errors fail safely; no other provider fallback or SMS network adapter is used. Owner-approved registration-style and forgot-password OTP emails were accepted by Gmail SMTP and receipt was confirmed. The forgot-password endpoint test used a temporary verified account and challenge inside a transaction that was rolled back; no password was reset and no test records remain.
- Kept hashed six-digit OTPs, expiry/attempt/resend enforcement, email-only customer login, staff-only operations login, generic email recovery, CSRF/session endpoints, and session invalidation after reset.
- Added React registration, verification, customer login, recovery, password reset and permission-aware operations dashboard routes connected to the protected APIs.
- Registration account-enumeration fix: new, duplicate-identifier, and delivery-failure registration attempts share a generic HTTP 201 response structure. Duplicate submissions preserve database uniqueness, create no account/challenge, and send no OTP. Added response-equivalence, side-effect and minimum-duration (1.0 second) regression tests.
- Added fail-fast Django startup validation for an empty or example-placeholder `DJANGO_SECRET_KEY`, with three regression tests.
- Released under commit `77780e76cd9ce5b496856f9b3f5f768e7ce699cc`.

## [Phase 9] - Public contact page and enquiry compatibility

- Added canonical React `/contact/` routing that reuses the existing `EnquiryPage`, unchanged `/api/v1/enquiries/` submission contract, and product/category preselection.
- Added `/enquiry/` and `/enquiry` compatibility redirects that preserve query parameters and URL fragments while routing to `/contact/`.
- Updated canonical public header, footer, homepage, catalogue, and product-detail links to `/contact/`; no company details, products, certifications, availability, or commercial claims were invented.
- Added an unpublished [privacy-policy framework](docs/PRIVACY_POLICY_FRAMEWORK.md) marked owner-review-required, with no public policy route, consent field, migration, or Gmail enquiry notification.
- Added Vitest/Testing Library route and payload regression tests. Phase 9 verification passed 3 frontend tests, frontend lint, and production build, plus 85 isolated-SQLite backend tests, Django checks, and migration drift checks.
- Released under commit `f1e700eab29756580d1dec7ad17344a38158a042`.

## [Phase 10] - Custom React staff enquiry dashboard

- Added protected `/operations/enquiries` inbox and enquiry-detail routes.
- Added staff-only list/detail/PATCH API behavior under `/api/v1/operations/enquiries/`, with separate `view_exportenquiry` and `change_exportenquiry` permissions, Django session authentication, CSRF on writes, four validated statuses (`new`, `in_progress`, `responded`, `closed`), pagination, filtering, search, internal-note updates, and no delete method.
- Separated minimized list serialization from private authorized detail serialization; email, phone, message, and internal notes are not returned in the inbox list. Public enquiry submission remains unchanged.
- Kept Django Admin available and disabled enquiry deletion. Added React route/permission guards and responsive inbox/detail presentation without sensitive browser storage.
- Verification passed 93 isolated-SQLite backend tests, Django checks, migration-drift checks, 6 Vitest frontend tests, frontend lint, and production build.
- Released under commit `e388bb3fe61744475c42c8ec4b0c07d845e59561`.

## [Phase 11] - Farm and Crop Season operations dashboard

- Added dedicated React list, detail, create, and edit workflows for Farms and Crop Seasons under `/operations/farms` and `/operations/crop-seasons`, preserving session authentication, CSRF writes, Django model permissions, Django Admin fallback, and unrelated generic operations routes.
- Added validated `farm_reference` filtering to the Crop Season collection API with backward-compatible pagination metadata and dedicated valid, invalid, blank, unauthorized, and pagination coverage.
- Added responsive operations presentation, loading, empty/error, detail, row-action, pagination, permission, and historical-data feedback states. Added a controlled paginated Farm selector that preserves the selection and never downloads unlimited records.
- Verification passed 95 isolated-SQLite backend tests, Django system checks, migration drift checks, 9 Vitest tests, frontend lint, and production build.
- Released under commit `0f75950c1d72ad3ff78ad2e95b5eef4f2562d919`.

## [Phase 12] - Harvest operations management

- Added dedicated React list, detail, create, and edit routes for Harvest records under `/operations/harvests` while preserving session authentication, CSRF, model permissions, Django Admin fallback, and generic operations routes.
- Added validated `farm_reference` and `crop_season_reference` Harvest collection filters with AND semantics, standard pagination metadata, 404 handling for unknown references, and 400 handling for blank filters or Farm/Season mismatch.
- Added backend closed/cancelled CropSeason creation protection and model-level validation; existing records remain viewable, while existing historical ProductionBatch protection remains enforced and notes remain editable.
- Added proper `eligible_for_harvest=true/false` backend filtering before CropSeason pagination, removed the duplicate free-text Season input, and retained backend-supported `historical_locked` metadata.
- Automated testing passed: 100 complete isolated-SQLite backend tests via `python manage.py test` (99 within `api` plus settings security), 13 Vitest tests, frontend lint, and production build.
- Released under commit `ba06e2d69f51f62f6ea63386748bdbff1259cc58`.
