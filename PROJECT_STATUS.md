# Project Status

## Project status

**Phase 0 — foundation:** Complete and previously verified.

**Phase 1 — requirements and architecture:** Complete. Business and operational owner confirmations remain open before launch.

**Phase 2 — homepage and visual foundation:** Implemented and verified. Scope is limited to the public homepage, shared header/navigation/footer, visual tokens and responsive interactions. No product detail/catalogue route, working enquiry submission, business API, database schema, or backend application changes.

**Phase 3 — product catalogue and read API:** Implemented. The database contains six owner-provided category labels and zero product records. Public API and frontend catalogue routes are functional; no enquiry submission, quotation workflow, authentication feature, or payment behavior was added.

**Phase 4 — export enquiry system:** Implemented and locally verified. Category/product enquiries are stored for staff review; no email notification provider or multi-product quote workflow is configured. Production privacy/retention and distributed anti-abuse controls still require owner review.

**Phase 5 — admin product management and content workflow:** Implemented and locally verified. Authorized Django staff can create, edit, publish, unpublish and delete products with image previews and validated uploads. Product and category deletion is protected when related enquiries/products exist. No product records were created.

**Phase 6 — real product catalogue and content preparation:** Implemented. Added an owner-editable blank CSV intake template and verified-content/image guide, improved catalogue empty states, added route-aware SEO titles/descriptions, and clarified product-detail semantics. No products or schema changes were added; six categories and the existing enquiry were preserved.

**Phase 7 — own farm and crop traceability foundation:** Implemented. Added private farm, season, harvest, production batch, processing-event, and inventory-ledger models; Django Admin workflows; and paginated staff-only APIs. The reviewed additive migration is applied to `spiceora_db`; no farm or operational records were seeded.

**Phase 8 — email-first authentication and operations dashboard:** Complete and verified. Customer registration activates after email OTP only; validated mobile numbers remain unverified. Login and recovery use email only, and SMS is deferred. Personal Gmail SMTP is configured and owner-approved registration and forgot-password OTP receipts were confirmed; Gmail remains a low-volume testing option, not production-grade transactional email.

**Phase 9 — public contact page and enquiry compatibility:** Complete and pushed. `/contact/` reuses the existing enquiry form/API, while `/enquiry/` redirects preserve query parameters and fragments. The privacy policy remains an unpublished owner-review framework. No migration, database record change, consent field, or Gmail enquiry notification was added.

**Phase 10 — custom React staff enquiry dashboard:** Implementation resumed from the approved baseline and is currently for final review; not committed or pushed. The staff inbox/detail UI, staff-only enquiry API, permission separation, list/detail privacy, status/notes controls, Admin deletion protection, and regression coverage are implemented without migrations or application-record changes. Browser and final security review remain subject to the results below.

### Environment

- Windows, Python 3.12.10, Node.js 24.18.0, npm 11.16.0
- MySQL 8.0.46 service is running locally and TCP port 3306 is reachable.
- GitHub repository `https://github.com/maahin132/SPICEORA` is configured as `origin`; Phase 7 baseline was verified before this phase.
- Latest credential re-verification: 2026-10-28. The `.env` password was read only in process and was never displayed.

### Implemented

- React + Vite + Tailwind CSS 4 + React Router + Lucide React homepage, product catalogue, and product detail routes.
- Django 5.2 + Django REST Framework + PyMySQL configuration, environment loading, CORS configuration, `/api/health/`, read-only catalogue endpoints, and public enquiry creation.
- Phase 3 `ProductCategory` and `Product` models, Django admin maintenance, published-only API serializers, and optional product image uploads.
- Phase 4 `ExportEnquiry` persistence, field/product/category validation, quantity constraints, five-per-hour IP-based request throttling, opaque submission reference, and Django admin status/notes workflow.
- Phase 5 Django admin product/category content workflow, protected related-record deletion, product image preview and validated UUID-named image uploads.
- Phase 6 owner content intake guidance and six-row blank draft CSV; route-specific browser titles and meta descriptions use only approved catalogue name/summary fields, and empty catalogue pages provide an enquiry CTA.
- Phase 7 private traceability models, protected staff APIs, admin workflows, append-only processing/inventory records, and movement-derived stock calculations; no custom operations UI was added because the public frontend has no secure staff authentication/CSRF flow.
- Phase 8 Django account profile and hashed OTP challenge models, distinct customer/staff login, Gmail-only email delivery, email-only recovery, session/CSRF endpoints, account/IP throttles, and React authentication/operations routes. Mobile numbers are captured but explicitly unverified; SMS is disabled. Public registration cannot grant staff access.
- Product image uploads accept JPEG, PNG and WebP content up to 5 MiB and 8,000 px per side / 40 megapixels; existing image paths are retained. Local development media is supported; production image storage is not configured.
- React `/enquiry/` form with accessible labels, client/server validation, duplicate-submit prevention, pending/success/error states, and product-specific preselection from detail pages.
- Root `.env` contains local Django/database settings and is ignored by Git. Django now uses `DB_HOST=localhost`, matching the MySQL account whose password is in `.env`.
- `.env.example`, setup guides, architecture/API/database/security/testing/deployment/roadmap docs, and GitHub issue/PR templates.
- Local Git `main` branch initialized with the supplied GitHub URL as `origin`.

### Phase 8 authentication and operations foundation

- The existing Django auth user model is preserved. `AccountProfile` adds unique normalized email/mobile and independent verification flags; `OTPChallenge` stores hashed six-digit codes and challenge state. Public registration creates inactive non-staff accounts and activates after email verification only. The API reports `mobile_verified=false`; there is no mobile-login or mobile-verification path that can mark it true.
- Email is restricted to personal Gmail SMTP (`smtp.gmail.com:587`, TLS) using a Google App Password; no generic SMTP fallback or other provider is allowed. This is a low-volume testing option, not production-grade transactional email; Google may rate-limit or block sending. SMS is disabled, makes no network calls, and SMS recovery requests are rejected. Email recovery remains generic; staff-only provider health reports readiness only.
- Added generic recovery initiation, separate customer/staff session login, current-user/logout/CSRF endpoints, password reset and session invalidation. Existing staff role and model-permission gates are unchanged.
- OTP lifetime is five minutes, max incorrect attempts is five, codes are single-use, and resend cooldown is 60 seconds. IP-scoped and hashed account-identity throttles apply. The local-memory cache is not suitable for production multi-worker abuse controls.
- Added React routes `/register`, `/verify/email`, `/verify/mobile`, `/login`, `/forgot-password`, `/forgot-password/verify`, `/new-password`, `/operations/login`, `/operations`, and staff-protected farm, season, harvest, batch, processing and inventory screens. Operations APIs enforce staff/model permissions; no token or password is stored in localStorage.
- Migration source/generated SQL for `api.0005_customer_account_otp` were reviewed and found additive (two new tables only); applied to `spiceora_db`. Post-migration counts were six categories, zero products, one existing enquiry, no farm/traceability rows, and no new profiles/challenges. No user or enquiry content was read or changed.
- Gmail SMTP is configured in the ignored repository-root `.env`; Django loaded the approved Gmail host/port, TLS, sender/login match, and App Password without displaying credential values. One registration-style OTP was accepted by SMTP and receipt was confirmed by the owner. The actual forgot-password endpoint was also exercised against an owner-approved inbox: a temporary verified customer and recovery challenge were created inside a database transaction, the endpoint returned 202 and SMTP accepted the message, and the transaction was rolled back. The owner confirmed receipt. No temporary account/challenge remains; no password reset was performed. SMS remains disabled. Gmail is suitable only for low-volume testing and is not a production delivery guarantee. Do not use a paid email/SMS service. Phase 8 remains uncommitted and unpushed for owner review.
- Registration account-enumeration fix: valid new, duplicate email/mobile, and email-delivery-failure submissions return the same generic HTTP 201 response shape. Duplicates and delivery failures do not create accounts/challenges or send OTPs; a random non-persisted challenge ID is returned. Database uniqueness constraints remain authoritative. Responses have a one-second minimum duration; synchronous SMTP can exceed it, so constant-time behavior is not claimed.

### Phase 8 verification (in progress)

| Check | Result |
|---|---|
| Pre-migration database target and record counts | Passed; target `spiceora_db`; six categories, zero products, one enquiry, zero Phase 7 operational rows |
| Migration source and generated MySQL SQL | Passed; two additive account/OTP tables, no existing table alteration or data migration |
| Migration application/state | Passed; `api.0005_customer_account_otp` applied; current schema matches models |
| Post-migration content preservation | Verified; category/product/enquiry/operations counts unchanged; new profile/challenge tables empty |
| Django checks | Passed; `check`, `check --database default`, `migrate --check`, and `makemigrations --check --dry-run` |
| Targeted email-first authentication tests | Passed; 23 auth tests within isolated SQLite suite; mocked email only and no SMS/network calls |
| Full backend suite | Passed; 85 tests using isolated SQLite |
| Frontend lint/build | Passed; `npm run lint` and `npm run build` |
| Browser/responsive QA | Passed for email-first registration safe-failure state, mobile-deferred page, email-only recovery/login labels, unauthenticated operations redirect, and staff dashboard on isolated SQLite. Registration page checked at 320, 390, 768, 1024 and 1440 CSS px without horizontal overflow. Full operations CRUD/error-state coverage remains pending. |
| Gmail SMTP configuration and registration OTP delivery | Passed; Django loaded Gmail settings with credentials withheld; one registration-style OTP was accepted by SMTP and receipt was confirmed by the owner. |
| Forgot-password live delivery | Passed; actual recovery-start endpoint returned 202 and SMTP accepted a password-reset OTP to the approved inbox; owner confirmed receipt. Temporary verified test account/challenge were rolled back; no password was reset. |
| SMS verification/recovery | Deferred and disabled; no SMS provider is called |
| Migration drift / MySQL check | Passed; no model changes detected, configured `spiceora_db` check passed, and no Phase 8 schema changes were made in this adjustment |
| Documentation / credential-pattern scan / `.env` check / diff whitespace | Passed; local Markdown links and high-confidence credential-pattern scan passed; `.env` remains ignored/untracked; `git diff --check` passed |
| Git commit/push | Intentionally withheld for owner review. Phase 8 remains uncommitted and unpushed. |

### Phase 1 planning deliverables

- [Business requirements](docs/BUSINESS_REQUIREMENTS.md): audience, goals, non-goals, six requested product-category labels, buyer journeys and owner-confirmation register.
- [Information architecture](docs/INFORMATION_ARCHITECTURE.md): lean sitemap, launch/deferred page recommendations, page sections, CTAs, data needs and mobile behavior.
- [Application architecture](docs/ARCHITECTURE.md): current-vs-proposed boundaries, request/data flow, validation/error handling and deployment decisions.
- [Database plan](docs/DATABASE.md): proposed catalog/enquiry entities and relationships; no schema was created.
- [API plan](docs/API.md): proposed public read and enquiry contracts and protected admin boundary; no endpoint was added.
- [Design system brief](docs/DESIGN_SYSTEM.md): owner-provided palette with editorial typography, photography, responsive and accessibility guidance; Phase 2 implementation is summarized below.
- [Security](docs/SECURITY.md), [testing](docs/TESTING.md), [deployment](docs/DEPLOYMENT.md), [roadmap](docs/ROADMAP.md), and this status record updated to distinguish current controls from proposals.

### Phase 1 verification

| Check | Result |
|---|---|
| Markdown relative links | Passed; 14 Markdown files checked, no broken relative links |
| Django `check` | Passed; no issues |
| Django `check --database default` | Passed |
| Django `migrate --check` | Passed; no pending migrations |
| Django backend tests | Passed; 1 test |
| Application/schema/dependency changes | None; Phase 1 is documentation only |
| `.env` | Ignored and untracked; secret values were not printed or included in documentation |
| GitHub | Phase 1 documentation commit was pushed and verified on remote `main` |

### Phase 2 implementation

- Replaced the Phase 0 placeholder screen with an editorial home page using the approved palette and responsive layout.
- Added shared SPICEORA header/desktop navigation, keyboard-operable mobile menu (Escape closes and restores focus), skip link and shared footer.
- Added six illustrative spice-category cards, brand introduction, clearly labelled proposed enquiry path, and a contact placeholder.
- Added local Unsplash still-life image with license noted in [design system](docs/DESIGN_SYSTEM.md), honest captions, image load fallback, and responsive image crops. It does not imply actual stock or product specifications.
- Added Tailwind CSS v4 design tokens, responsive component styles, visible keyboard focus and reduced-motion handling.
- The enquiry section does not accept or send submissions; no backend endpoint exists. No company email, phone, address or social link was invented.

### Phase 2 verification

| Check | Result |
|---|---|
| `npm run build` | Passed |
| `npm run lint` | Passed (`oxlint`) |
| Browser homepage check | Passed; page rendered with all six categories and all 7 local image instances loaded |
| Browser mobile menu | Passed; opens, `aria-expanded` updates, Escape closes and restores focus, and section navigation closes the menu |
| Responsive viewport smoke check | Passed at 320, 390, 768, 1024, and 1440 requested widths; no horizontal overflow after 320px fix |
| Image fallback | Passed; broken hero image switches to an accessible visual fallback with its informative text alternative |
| Not-found route | Passed; unknown URL shows the not-yet-built route state |
| Contrast spot checks | Passed; updated small-copy pairs range 4.76:1–5.30:1, and the focus ring on forest is 6.74:1 |
| Homepage/enquiry honesty | Passed; contact section clearly states submissions are not accepted |
| Django tests | Not rerun; backend implementation was unchanged in Phase 2 |
| Frontend automated component tests | Not available; no frontend test runner is configured |
| Markdown links and `git diff --check` | Passed; 15 Markdown files checked, no broken relative links |
| Secrets | `.env` remains ignored/untracked; no secret values were added to frontend assets or staged documentation |

### Phase 3 implementation

- Added `ProductCategory` (unique name/slug, display order, active state) and `Product` (category FK, unique slug, approved name/summary/description, optional image/alt text, published state, display order, timestamps). Product publication defaults off.
- Added six owner-provided category label records. No product/demo records, prices, specifications, inventory, origin claims, or certifications were created.
- Added searchable/filterable Django admin category and product screens. Phase 3 initially limited product images to 5 MiB and JPG/JPEG/PNG/WebP; Phase 5 adds content/extension matching and dimension limits.
- Added public `GET /api/v1/categories/`, paginated `GET /api/v1/products/` with validated `category` filtering, and `GET /api/v1/products/{slug}/`. Inactive categories and unpublished products are excluded.
- Added React `/products/` and `/products/:slug/` routes, API-driven homepage preview, category filter, pagination, loading/empty/error/not-found states, and reusable product cards.
- Development Vite proxy supports `/api` and `/media`. Production media storage is not configured.
- The enquiry section remains non-submitting; Phase 4 has not started.

### Phase 3 verification

| Check | Result |
|---|---|
| Configured database target | Confirmed `spiceora_db` at `localhost`; both catalogue tables use `utf8mb4_0900_ai_ci`; secrets were not displayed |
| Pre-migration schema inspection | Existing Django/auth tables only; no catalogue tables |
| Migration review | `api.0001_initial` creates only `api_productcategory` and `api_product` and inserts six confirmed category labels; no product rows or destructive SQL |
| `python manage.py migrate api --noinput` | Passed against `spiceora_db` |
| Post-migration data/schema check | Passed; six categories, zero products, and only the two expected catalogue tables |
| `python manage.py check --database default` | Passed |
| `python manage.py migrate --check` | Passed; no pending migrations |
| `python manage.py makemigrations --check --dry-run` | Passed; no model/migration drift |
| Django API tests | Passed; 10 tests using isolated in-memory SQLite via `--settings=config.test_settings` |
| Frontend `npm run lint` | Passed |
| Frontend `npm run build` | Passed |
| Live API | Passed; direct and Vite-proxied product list, category list and `/products/` returned HTTP 200 |
| API validation | Passed; invalid category and page returned 400; absent product slug returned 404 |
| Browser catalogue | Passed; live empty state and mocked product card/detail/category filter; no horizontal overflow at 320, 390, 768, 1024, or 1440px |
| Browser route/link/image checks | Passed; product detail/breadcrumbs, 404 state, broken-image fallbacks, homepage behavior with API failure, and mobile menu were exercised; database remains free of product/demo records |
| `git diff --check` | Passed |
| Frontend automated component tests | Not configured; browser smoke checks used instead |
| Secret check and `.env` | Passed; `.env` remains ignored/untracked and values were not printed |

### Phase 4 implementation

- Added one `ExportEnquiry` record for a category or a single published product; product category is derived server-side and product name is snapshotted. Multi-item quotations are not supported.
- Required fields are full name, syntactically valid email, country, exactly one active category or published product, positive estimated quantity, and quantity unit. Company, phone and message are optional. Quantity must have up to three decimals. Supported units are kilograms and metric tonnes.
- Public API accepts JSON only, rejects unknown keys, stores records in MySQL, and returns only a generic confirmation and opaque UUID reference. There is no enquiry read endpoint and no email notification.
- Added Django admin search by name/email/company/country; status/date/category filters; and editable workflow status/internal notes. These values are not in public responses.
- Added responsive form and product-specific enquiry links that preselect the published product/category. The homepage, header and footer now route to the working form without inventing contact details.
- Added a five-requests-per-hour IP-based DRF throttle. The default local-memory cache is not shared across workers/hosts; production needs a shared cache, trusted-proxy review and edge controls.
- Privacy notice/consent, jurisdiction and retention/deletion policy, production email delivery and staff response operations remain owner-confirmation requirements.

### Phase 4 verification

| Check | Result |
|---|---|
| Migration source and SQL review | Passed; migration creates only `api_exportenquiry`, a positive quantity/unit check constraint, and FKs to the existing category/product tables; no destructive SQL |
| Database target before migration | Verified without exposing credentials: `spiceora_db` at `localhost`, MySQL 8.0.46; target table did not exist |
| `python manage.py migrate api 0002 --noinput` | Passed; applied only `api.0002_exportenquiry` |
| Post-migration database inspection | Passed; table collation `utf8mb4_0900_ai_ci` and constraint present; six categories, zero products, and one enquiry row at final inspection. The enquiry row was preserved because its provenance could not be verified |
| `python manage.py check` / `check --database default` | Passed |
| `python manage.py migrate --check` / `makemigrations --check --dry-run` | Passed; no pending migration or model drift |
| `python manage.py test --settings=config.test_settings` | Passed; 23 tests on isolated in-memory SQLite, including submission validation, visibility, internal-field protection, model constraints, admin status/notes, and throttling |
| Frontend `npm run lint` | Passed without warnings |
| Frontend `npm run build` | Passed |
| Live dev endpoints | Passed; `/enquiry/` and `/api/v1/categories/` returned HTTP 200 |
| Browser product-specific enquiry | Passed; product detail CTA opens `/enquiry/` with the product and category selected; mocked product read used, and product selection can be removed |
| Browser form success/error states | Passed with mocked HTTP responses; payload shape checked, required input labels/attributes and field-level error display checked. An initial mock attempt reached the local API and its identified test record was removed; a later final database inspection found one row whose provenance could not be verified, so it was preserved |
| Browser responsive check | Passed with no horizontal overflow at 320, 390, 768, 1024, and 1440 requested CSS-pixel widths |
| Live API sanity | Passed; active category list returned HTTP 200, empty JSON submission returned 400, and enquiry GET returned 405. One enquiry row was present at final inspection and was left untouched because its provenance could not be verified |
| Markdown links, staged diff, secret scan | Passed; 37 local links checked, staged diff reviewed, whitespace check passed, and secret-pattern scan found no matches |
| `.env` | Remains ignored and untracked; credentials were not printed or edited |

### Phase 5 implementation

- Reused the existing product/category fields; no product content, specifications, certifications, prices, stock, availability claims, or sample products were added.
- Improved Django Admin product list/search/filter/order fields, editable publication and display order, content/publication fieldsets, timestamps, and primary-image previews. Category management remains available in Django Admin.
- Product images must have matching JPEG/JPG, PNG, or WebP content and extension, be at most 5 MiB, and be no larger than 8,000 px on either side or 40 megapixels. New filenames are random UUIDs under `MEDIA_ROOT/products/`; existing stored paths are unchanged. Admin previews distinguish no image from a missing stored file.
- `ExportEnquiry.product` now uses `PROTECT`, preventing product deletion when an enquiry references it; category references were already protected. No Phase 4 enquiry was edited or deleted.
- Public catalogue routes and response fields are unchanged. Existing product cards/detail pages continue to use uploaded image URLs with a browser-level graceful fallback; the product detail image loads eagerly.
- Production media hosting, CDN, image scanning, backup/retention and delivery policy remain unconfigured.

### Phase 5 verification

| Check | Result |
|---|---|
| Pre-migration database inspection | Verified target `spiceora_db` / MySQL 8.0.46; six categories, zero products, one enquiry, and no enquiry linked to a product |
| Migration source and SQL review | Passed; `api.0003_phase5_product_admin_safety` changes ORM deletion behavior and upload path/validators only; `sqlmigrate` reported no SQL operations |
| Migration application/state | Passed; applied `api.0003_phase5_product_admin_safety`; no pending migration |
| Post-migration database inspection | Passed; existing category/product/enquiry counts and enquiry-product link count unchanged; enquiry record was not read, altered, or deleted |
| Django system and database checks | Passed |
| Isolated Django tests | Passed; 34 tests cover admin product create/update/publish/unpublish/delete confirmation, category filtering, unpublished visibility, safe image upload/validation/preview/API URL, category/product/enquiry deletion protection, and Phase 4 behavior |
| Frontend lint and production build | Passed |
| Public API route checks | Passed; category and paginated product lists work, detail returns 404 for absent/unpublished products, and product image URLs remain public absolute URLs when present |
| Browser responsive and route checks | Passed; live empty catalogue, category filter, and missing-product detail checked at 320, 390, 768, 1024, and 1440 px with no horizontal overflow. No approved products exist, so a real published-product image/detail rendering was unavailable; the existing shared image fallback is unchanged |
| Markdown links, staged diff, secret scan | Passed; no secret patterns; `.env` remains ignored and untracked |

### Phase 6 content and catalogue preparation

- Added [`docs/product-content-intake-template.csv`](docs/product-content-intake-template.csv) with one blank draft row for each of the six existing category labels. The file is an owner intake tool only, is not imported automatically, and created no product rows.
- Added [`docs/PRODUCT_CONTENT_PREPARATION.md`](docs/PRODUCT_CONTENT_PREPARATION.md) with required core content, optional owner-evidence fields, publication gate, image specifications, naming and alt-text guidance.
- No extra database fields, migrations, product records, image assets, or unsupported product claims were added.
- Improved the homepage and catalogue empty state with a truthful status and enquiry route; category filtering stays on the existing accessible category select and query-string URL behavior.
- Product-detail content now labels the description section semantically. Route-specific page titles and meta descriptions use page context; published product title/summary come from the API. Descriptions are capped for metadata, no unknown product structured data or production canonical domain is generated. Metadata updates client-side; the initial HTML is generic and SSR/prerendering is not configured.
- Product URL pattern remains `/products/{slug}/`; product-to-enquiry CTA continues to include the published product and category slugs. Product image alt text remains owner supplied and required on admin upload; the existing fallback is retained and resets correctly when the image source changes.

### Phase 6 verification

| Check | Result |
|---|---|
| Database inspection | Verified `spiceora_db`; six categories, zero products, one existing enquiry and zero product-linked enquiries. No enquiry contents were read or changed |
| Database/schema changes | None; no model changes or migrations |
| Content intake CSV | Passed; valid CSV structure, six exact existing category labels, blank product/content/optional fields, all rows draft and unverified |
| Django checks and isolated backend suite | Passed; 34 tests using in-memory SQLite |
| Migration state | Passed; Phase 5 migrations current and no drift |
| Frontend lint/build | Passed |
| Public API and category filtering | Passed; six categories, empty product results, category filter empty result, and absent detail returns 404 |
| Browser page metadata and empty-state checks | Passed; homepage, catalogue, enquiry and missing-product routes update title/description; catalogue and homepage empty-state CTAs work; category-prefilled enquiry link and filter clearing work |
| Browser responsive check | Passed; homepage, catalogue and missing-product detail had no horizontal overflow at 320, 390, 768, 1024 and 1440 CSS pixels |
| Published-product detail/image visual check | Not possible without owner-approved product records; no test product was created. The existing shared missing-image fallback remains available, but a real published image could not be visually verified |
| Markdown links | Passed; 48 local links across 11 documents |
| Staged diff and secret scan | Passed; 20 intended Phase 6 files reviewed, no secret patterns found, and `.env` remains ignored and untracked |
| `.env` | Remains ignored and untracked; no values printed or changed |

### Phase 7 farm-to-inventory foundation

- Farm/crop/harvest/batch/processing/inventory workflow is implemented in Django. Crop names and operation references are staff-entered. No operational records, facility claims, certification claims, or production capabilities were fabricated.
- Batches are traced to harvest, crop season, and farm. Batch creation atomically records an initial production receipt, and harvest allocation prevents batch totals from exceeding harvested quantity.
- Inventory is computed in kilograms from immutable movements. Reservations reduce available stock; releases restore it; dispatch consumes pooled reservations first; approval-gated corrections are additional movements. Negative available or physical stock is rejected, and movement dates cannot be backdated behind existing movements.
- Internal API access is staff-session authenticated, per-model permission gated, CSRF protected on writes, paginated, and limited to list/create. Corrections require the additional `approve_inventory_correction` permission. The React app does not expose operations data.
- Migration source/SQL review found six additive new tables, check constraints, and protected foreign keys only. No existing table/row was modified or deleted; no new operational records were inserted.
- Exact post-migration record counts, test results, frontend/browser checks, secret scan, and Git verification are recorded below after final verification.

### Phase 7 verification

| Check | Result |
|---|---|
| Pre-migration database target | Passed; configured and connected database `spiceora_db`, MySQL 8.0.46 |
| Migration source and SQL review | Passed; migration creates six traceability tables with constraints and FKs only; no destructive DDL/DML or data seeding |
| Migration application | Passed; `api.0004_farm_cropseason_harvest_productionbatch_and_more` applied |
| Post-migration database counts | Verified six categories, zero products, one existing enquiry, and zero rows in each of the six new operational tables |
| Django checks and migration drift | Passed; `check`, `check --database default`, `migrate --check`, and `makemigrations --check --dry-run` |
| Backend isolated suite | Passed; 58 tests using in-memory SQLite (34 baseline plus 24 Phase 7 tests); MySQL concurrency is not established by SQLite |
| Frontend lint/build | Passed; no Phase 7 frontend code was needed |
| Protected API/admin verification | Passed in isolated tests; staff/model permissions, CSRF write enforcement, correction approval, admin read-only ledger, and full API lineage tested |
| Responsive/browser checks | Passed; existing public routes checked at 320, 390, 768, 1024 and 1440 px without horizontal overflow; category selection and enquiry prefill verified; admin login loaded and unauthenticated operations API access returned 403 |
| Secret scan and `.env` | Passed; no high-confidence credential patterns in staged changes; `.env` is ignored and untracked |
| Git identity and remote | Verified before commit; configured author/committer are Maahin and `origin` points to the SPICEORA GitHub repository |

### Verification results

| Check | Result |
|---|---|
| Frontend dependency installation | Passed; npm reported 0 vulnerabilities in both install steps |
| `npm run build` | Passed |
| `npm run lint` | Passed |
| Frontend dev server | Passed; `http://127.0.0.1:5173/` returned HTTP 200 |
| `python manage.py check` | Passed on 2026-10-28; no issues |
| `python manage.py check --database default` | Passed on 2026-10-28 using the actual local `.env` credentials |
| `python manage.py test` | Passed on 2026-10-28; 1 health endpoint test |
| Django health endpoint | Previously passed; `/api/health/` returned HTTP 200 with `{"status":"ok"}` |
| MySQL service and TCP 3306 | Passed |
| Database creation | Passed; `spiceora_db` created with `utf8mb4` |
| Application user host configuration | Authenticated Workbench inspection found unlocked `caching_sha2_password` accounts for both `localhost` and `127.0.0.1`; their password hashes differ |
| Authentication diagnosis | The password in `.env` authenticated as `spiceora_app@localhost` and failed as `spiceora_app@127.0.0.1` with error 1045 |
| Django MySQL connection check | Passed after changing only local `.env` `DB_HOST` from `127.0.0.1` to `localhost` |
| Django migrations | Passed; `migrate --noinput` reported no migrations to apply, and `migrate --check` passed |
| GitHub push | Passed; the re-verification documentation update was pushed and matched `origin/main` |

No database, account, password, or grant was changed during this fix. `woodhub_db` was not accessed or changed. `.env` remains ignored; no secret values were printed, staged, committed, or pushed.

### Phase 1 decisions and proposals

- **Confirmed by owner brief:** premium customer-facing Indian spice-export B2B website; target buyers are international B2B buyers, importers, distributors, wholesalers and related business customers; working tagline “From Indian Origins to Global Markets.”; requested categories Cumin, Fennel, Red chilli, Turmeric, Coriander, Dhana-jeera; existing React/Vite, Django REST Framework and MySQL stack.
- **Proposed:** lean multi-page catalogue and enquiry website; combine contact/export/quotation intents into one buyer form; no account, checkout, dashboard, ERP or marketplace; publish only active, owner-approved products; prefer same-origin deployment; use Django admin for protected staff operations; add multi-product enquiry items only if owner confirms the need.
- **Original design direction:** editorial export-house identity using the requested forest green `#203B30`, warm ivory `#F7F3E9` and muted gold `#C49A55`, real rights-cleared imagery, deliberate typography and restrained motion.

### Owner confirmation required before implementation/content launch

- Legal/display company identity and public contact details.
- Actual available products per category; product descriptions, images, origin/specification/quality statements and any certifications or proof.
- Export markets/process, documents, packaging, quantities, incoterms, shipping, payment, pricing, lead times and response expectations.
- Enquiry field requiredness, single/multi-product quote behavior, recipient/staff workflow and retention/deletion policy.
- Applicable privacy jurisdiction, controller, lawful basis, notice, hosting/data region and user-rights process.
- Brand assets, image/font licensing, language/currency needs, domain, hosting provider and operational owners.

## Phase 1 outcome

Phase 1 deliverables remain documented as decisions, proposals and open owner questions. Phases 2–7 are implemented; Phase 8 is in progress and remains blocked on real email/SMS delivery verification and final browser/security checks. Contact details, publishable product content and images, optional product claims/evidence, privacy/retention policy, production abuse controls, staff assignments, and operational policies remain owner-confirmation items. Do not start Phase 9 without explicit owner approval.
