# Testing Plan

## Current foundation checks

From `backend/` with the virtual environment active:

```powershell
python manage.py check
python manage.py check --database default
python manage.py migrate --check
python manage.py test --settings=config.test_settings
```

The system and database checks use the local MySQL database configured by `.env`. The API tests use the in-memory SQLite test settings to keep test data isolated and avoid creating a separate MySQL test database; all test data is discarded. The suite covers public catalogue listing/filtering, enquiry submission/validation, quantity rules, product/category visibility, response field exposure, rate limiting, admin product creation/update/publication/deletion, protected product/category/enquiry relationships, image format/size/dimension validation, randomized image uploads and URLs, admin image previews, enquiry status/note management, and image alternative-text validation.

Phase 7 backend tests additionally cover farm/season/harvest date and quantity validation, harvest-to-batch allocation and immutable lineage, automatic initial receipts, processing record validation/immutability, kilograms/metric-tonne normalization, reservations/releases/dispatches, stock protection, movement append-only chronology, protected foreign keys, staff/model permissions, correction approval permission, CSRF enforcement, paginated operations responses, admin visibility, and end-to-end staff API traceability. Run these on the isolated SQLite test database; production MySQL row-lock concurrency is not verified by those tests.

Phase 8 authentication tests cover CSRF enforcement, email-only registration and activation, mobile-unverified state, duplicate email/mobile privacy, matching registration response status/shape, absence of OTP delivery or account/challenge creation for duplicates, registration response timing floor, E.164 number validation, single-use/expired/attempt-limited OTPs, resend cooldown, verified-email-only login, rejection of mobile login and SMS recovery, customer/staff separation, per-model operations permissions, generic email recovery, password reset/session invalidation, missing/example Django secret-key rejection, missing Gmail SMTP credentials, provider allowlisting, and safe SMTP errors. Email delivery is mocked; tests never send SMS or make provider network calls. These tests verify application behavior, not real email delivery. The timing test uses mocked, fast delivery and does not establish constant-time behavior against variable real SMTP latency.

From `frontend/`:

```powershell
npm run lint
npm run build
```

Phase 9 frontend verification uses Vitest, jsdom, React Testing Library, and user-event. Automated tests cover canonical `/contact/` rendering, `/enquiry/` legacy-query/hash preservation, product preselection, unchanged enquiry payload fields, and absence of consent/privacy-version fields.

Browser regression integration was completed against an isolated SQLite test database. It verified the canonical contact page, legacy `/enquiry/` query/hash redirect, product/category preselection, HTTP 201 success with an opaque receipt, HTTP 400 server validation, corrected retry success, double-click protection with one POST request, and non-exposure of private enquiry fields. A `GET /api/v1/enquiries/` request returned HTTP 405, confirming no public list/read operation. The isolated database and its temporary settings/data were removed after testing.

Browser regression should also cover the public homepage, catalogue, product detail, canonical `/contact/`, legacy `/enquiry/`, and protected operations routes. Responsive layout checks remain required at 320, 390, 768, 1024, and 1440 px, including pending/success/error states, navigation behavior, loading/empty/error/not-found states, image fallback, keyboard behavior, and mobile-menu focus behavior.

## Proposed tests before public launch

### Backend

- Catalog query/serializer tests: active-only visibility, category filtering, stable slug lookup, unpublished/missing product handling.
- Enquiry serializer/service tests: each intent, required/optional fields, bounds/format checks, rejected unknown/inactive products, multi-item behavior if approved, and transactional rollback on failed item insert.
- API tests: success/status/error contract, anonymous access limited to public operations, no enquiry read/list exposure, and no leakage of internal fields.
- Security/abuse tests: configured rate limiting, oversized body rejection, generic server errors, logging redaction, CSRF/session policy, and exact-origin CORS behavior.
- Admin tests: permissions for catalog and enquiry status changes; unauthorized staff cannot read/update enquiries.
- MySQL integration tests on the supported MySQL version and collation; migration forward test and backup/restore rehearsal.

### Frontend

- Route and not-found behavior; loading, empty, and error states for catalogue content.
- Product category navigation and product-to-enquiry prefill.
- Accessible form labels, keyboard use, focus/error announcements, validation, pending/success/failure states.
- Responsive viewport tests, image alternatives/captions, contrast and reduced-motion behavior.
- API contract tests, with no customer PII in client logs or analytics.

### Release checks

Run dependency/security scanners and static checks, review secrets/artifacts, test production configuration with `DEBUG=false`, and verify HTTPS, cookies, headers, CORS/CSRF, rate limits, logs, retention and restores in the deployed environment. No planned feature should be described as tested until its tests exist and pass.

The product catalogue, public read APIs, and enquiry submission are implemented. Before launch, add frontend automated interaction tests and execute production deployment/security checks, including rate-limit behavior with the configured shared cache and edge controls.

Phase 6 content preparation uses a six-row CSV intake template. Validate its header and category labels, and ensure the rows remain blank draft prompts rather than fixtures. Browser checks should verify the empty catalogue enquiry CTA, category-prefilled enquiry link, route-specific title/description updates, product detail 404 metadata, and the existing image fallback without inserting a product into the local database.

Phase 8 adds customer authentication and an operations area. Browser QA should exercise the public pages plus registration, email verification, login/recovery forms, staff-only route guards, operations collection loading/empty/error/create/edit states at 320, 390, 768, 1024 and 1440 CSS pixels. SMS is deferred; do not test with or call an SMS provider. Do not treat mocked email as proof of provider delivery, and do not create farm/harvest/batch/inventory data in the configured MySQL database for QA.

### Phase 8 browser QA executed

The local Vite frontend was exercised against a temporary Django server backed by a separate SQLite file outside the repository; the configured MySQL database was not used for browser fixtures. After the email-first adjustment, browser checks covered the registration form and safe missing-provider response, mobile-verification-deferred page, email-only recovery and login labels, unauthenticated operations redirect, and staff dashboard. Registration showed no horizontal overflow at 320, 390, 768, 1024 and 1440 CSS pixels. Earlier checks also covered the farm list empty state, catalogue empty state/enquiry CTA, and missing-product state. No farm, harvest, batch or inventory records were created. Full operations CRUD/error-state coverage remains unverified.

### Phase 8 live email delivery checks

The configured repository-root `.env` was loaded by Django. Configuration was checked using boolean/status output only: Gmail provider, approved host and port, TLS, configured login/App Password/sender, matching sender and login, and email readiness; no credential values were displayed. SMS readiness remained false.

Two controlled real-delivery checks were performed to the owner-approved test inbox: one registration-style OTP email sent through the delivery adapter, and one forgot-password OTP initiated through the actual recovery-start API endpoint. Gmail SMTP accepted both messages, and the owner confirmed receipt of each. For the recovery endpoint test, a temporary verified customer and its OTP challenge were created inside a transaction and explicitly rolled back after the endpoint returned HTTP 202 and a challenge was confirmed. No test account/challenge persisted and no password reset was performed. These checks confirm receipt for this test inbox at that time, not production deliverability or future availability.

The full backend suite separately passed with 85 tests on isolated SQLite; email is mocked in automated tests and they do not call an external provider or send SMS. Django system checks passed. Frontend `npm run lint` and `npm run build` passed. No commit or push was performed.
