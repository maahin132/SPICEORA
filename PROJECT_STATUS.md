# Project Status

## Project Status Overview

| Phase | Milestone Name | Status | Verified Git Commit / Reference |
|:---:|---|:---:|---|
| **Phase 0** | Project Foundation & MySQL Connection | **Complete & Verified** | `5a399d1` / `2bbce88` |
| **Phase 1** | Requirements, Architecture & Planning | **Complete & Verified** | `9795af2` |
| **Phase 2** | Editorial Homepage & Visual Foundation | **Complete & Verified** | `18b833c` |
| **Phase 3** | Database-Backed Product Catalogue & Read API | **Complete & Verified** | `63020e6` |
| **Phase 4** | Export Enquiry System & Rate Limiting | **Complete & Verified** | `827a007` |
| **Phase 5** | Admin Product Management & Safe Image Uploads | **Complete & Verified** | `3e32230` |
| **Phase 6** | Real Content Intake Template & Catalogue Guidance | **Complete & Verified** | `41f95f3` |
| **Phase 7** | Farm-to-Inventory Traceability Foundation | **Complete & Verified** | `5ee6786` |
| **Phase 8** | Email-First Auth, Gmail OTP & Staff Console | **Complete & Verified** | `77780e76cd9ce5b496856f9b3f5f768e7ce699cc` |
| **Phase 9** | Canonical Public Contact Page & Query Redirects | **Complete & Verified** | `f1e700eab29756580d1dec7ad17344a38158a042` |
| **Phase 10** | Custom React Staff Enquiry Inbox & Detail Dashboard | **Complete & Verified** | `e388bb3fe61744475c42c8ec4b0c07d845e59561` |
| **Phase 11** | Farm & Crop Season Operations Management UI | **Complete & Verified** | `0f75950c1d72ad3ff78ad2e95b5eef4f2562d919` |
| **Phase 12** | Harvest Operations Management & Historical Locks | **Complete & Verified** | `ba06e2d69f51f62f6ea63386748bdbff1259cc58` |
| **Phase 13** | Documentation Overhaul & Navigation Upgrade | **Documentation implementation complete — release pending** | Working tree at baseline `3bf656f9` before Phase 13 release commit |

---

## Environment & Configuration

* **Operating System:** Windows 10/11, Python 3.12.10, Node.js 24.18.0, npm 11.16.0.
* **Database:** MySQL 8.0.46 service running locally; port 3306 reachable.
* **Remote Repository:** `https://github.com/maahin132/SPICEORA` (`main` branch).
* **Local Secrets:** Stored in repository-root `.env` (strictly ignored and untracked by Git).
* **Database Connection Target:** `spiceora_db` at `DB_HOST=localhost` using `spiceora_app`. (Using `localhost` avoids MySQL 8 `caching_sha2_password` authentication failure 1045 observed with `127.0.0.1` on Windows).

---

## Implemented Features Inventory

* **Frontend (React 19 + Vite 8 + Tailwind CSS 4):**
  * Responsive editorial homepage, shared header with keyboard-operable disclosure navigation, and semantic footer.
  * Published-only product catalogue (`/products/`) with dynamic category filtering and product detail pages (`/products/:slug/`).
  * Canonical B2B enquiry route (`/contact/`) with product-context prefill and legacy `/enquiry/` redirects.
  * Customer authentication views: registration (`/register`), email OTP verification (`/verify/email`), mobile deferred notice (`/verify/mobile`), login (`/login`), password recovery (`/forgot-password`, `/forgot-password/verify`, `/new-password`).
  * Protected Staff Operations Dashboard (`/operations/*`):
    * Enquiry inbox and detail view with status/notes triage (`/operations/enquiries`).
    * Farm management list, detail, creation, and editing (`/operations/farms`).
    * Crop Season list, detail, creation, and editing with paginated Farm selector (`/operations/crop-seasons`).
    * Harvest list, detail, creation, and editing with closed-season creation guard and historical-lock indicators (`/operations/harvests`).
* **Backend (Django 5.2 + Django REST Framework):**
  * 30 distinct API route patterns covering public catalogue, enquiry submission, CSRF/session auth, staff enquiry management, and operations collections.
  * Models: `ProductCategory`, `Product`, `ExportEnquiry`, `Farm`, `CropSeason`, `Harvest`, `ProductionBatch`, `ProcessingRecord`, `InventoryMovement`, `AccountProfile`, `OTPChallenge`, and built-in `auth.User`.
  * Multi-layer permissions: staff session authentication, Django model permissions (`view_*`, `add_*`, `change_*`), CSRF write enforcement, and `approve_inventory_correction` for ledger corrections.
  * Validation: UUID-based image upload naming, file content/extension verification, E.164 phone validation, PBKDF2 OTP hashing, 5-minute expiry, 5-attempt lockout, and anti-enumeration timing floors.

---

## Detailed Implementation & Verification History

### Phase 0 — Technical Foundation & Database Connectivity
* Bootstrapped React/Vite and Django/DRF foundations.
* Created MySQL database `spiceora_db` and verified connection under `utf8mb4_0900_ai_ci`.
* Diagnosed host-specific authentication behavior on Windows, establishing `DB_HOST=localhost` in `.env`.
* Configured `/api/health/` liveness check.

### Phase 1 — Requirements & Architecture Planning
* Formulated B2B buyer journeys, operational non-goals, and editorial visual brief.
* Established the core rule: **Never publish unverified claims, unverified products, or unverified supplier data**.
* Outlined the owner-confirmation register for launch gating.

### Phase 2 — Homepage & Visual Foundation
* Implemented responsive editorial homepage using Tailwind CSS v4 design tokens (`#203B30` Forest Green, `#F7F3E9` Warm Ivory, `#C49A55` Muted Gold).
* Built accessible mobile menu disclosure with Escape key and focus-restoration handling.
* Sourced local rights-cleared illustrative photography with accessible visual fallbacks.

### Phase 3 — Product Catalogue & Read API
* Added `ProductCategory` and `Product` models with Django Admin workflows and image uploads.
* Seeded the six confirmed candidate category labels: *Cumin*, *Fennel*, *Red chilli*, *Turmeric*, *Coriander*, and *Dhana-jeera*.
* Preserved catalogue honesty: **Zero product records seeded**; empty states provide clear enquiry paths.
* Created anonymous read endpoints `GET /api/v1/categories/`, `GET /api/v1/products/`, and `GET /api/v1/products/{slug}/`.

### Phase 4 — Export Enquiry System
* Created `ExportEnquiry` model and public endpoint `POST /api/v1/enquiries/`.
* Implemented positive quantity validation, kg / metric tonne unit pairing, and opaque UUID receipt responses.
* Enforced 5 requests/hour/IP rate limiting via DRF throttling.
* Integrated product-specific enquiry preselection from catalogue detail pages.

### Phase 5 — Admin Product Content Workflow & Upload Safety
* Added Django Admin primary-image previews, sort order, and publication controls.
* Added server-side image validation: matching MIME/extension, max 5 MiB, max 8,000 px per side, max 40 megapixels, and random UUID storage filenames.
* Protected `Product` and `ProductCategory` records from deletion when referenced by enquiries or products.

### Phase 6 — Content Intake Preparation
* Added [`docs/product-content-intake-template.csv`](docs/product-content-intake-template.csv) containing blank draft prompts for the six categories.
* Authored [`docs/PRODUCT_CONTENT_PREPARATION.md`](docs/PRODUCT_CONTENT_PREPARATION.md) specifying verified photography, alt-text, and specification standards.
* Added route-aware browser titles and meta descriptions using API data.

### Phase 7 — Farm-to-Inventory Traceability Foundation
* Created additive operational schema: `Farm`, `CropSeason`, `Harvest`, `ProductionBatch`, `ProcessingRecord`, and `InventoryMovement`.
* Implemented append-only immutable movement ledger; dynamically calculates on-hand, reserved, and available stock under batch row locks.
* Exposed protected `/api/v1/operations/` endpoints requiring Django staff session authentication and model permissions.

### Phase 8 — Email-First Authentication & Operations Console
* Released under commit `77780e76cd9ce5b496856f9b3f5f768e7ce699cc`.
* Extended Django auth user with `AccountProfile` and `OTPChallenge` models.
* Configured personal Gmail SMTP (`smtp.gmail.com:587`, TLS) for low-volume testing; live delivery confirmed to owner test inbox for registration and password recovery.
* Enforced email OTP activation only; mobile numbers are captured in E.164 format but explicitly remain unverified; SMS is deferred.
* Implemented anti-enumeration protection: generic HTTP 201 responses with a 1.0-second minimum timing floor.
* Added fail-fast validation in Django settings rejecting empty or default example `DJANGO_SECRET_KEY`.

### Phase 9 — Public Contact Page & Query Redirects
* Released under commit `f1e700eab29756580d1dec7ad17344a38158a042`.
* Added canonical `/contact/` route reusing `EnquiryPage` and unchanged enquiry submission API.
* Added client-side redirects for `/enquiry/` and `/enquiry` preserving query parameters and URL hash fragments.
* Added unpublished [`docs/PRIVACY_POLICY_FRAMEWORK.md`](docs/PRIVACY_POLICY_FRAMEWORK.md) marked for owner review.

### Phase 10 — Staff Enquiry Dashboard
* Released under commit `e388bb3fe61744475c42c8ec4b0c07d845e59561`.
* Built custom React staff inbox and detail view at `/operations/enquiries`.
* Created staff-only endpoints `GET /api/v1/operations/enquiries/` and `GET, PATCH /api/v1/operations/enquiries/<uuid:public_reference>/`.
* Enforced list privacy: buyer email, phone, message, and internal notes are omitted from the inbox list and exposed only in authorized detail view.
* Enforced CSRF protection on status (`new`, `in_progress`, `responded`, `closed`) and internal note updates.

### Phase 11 — Farm & Crop Season Operations Management
* Released under commit `0f75950c1d72ad3ff78ad2e95b5eef4f2562d919`.
* Implemented dedicated React workflows for Farms (`/operations/farms`) and Crop Seasons (`/operations/crop-seasons`).
* Added validated `?farm_reference=` filtering on Crop Season collection API with standard pagination.
* Built controlled paginated Farm selector with persistent selection state across pages.

### Phase 12 — Harvest Operations Management
* Released under commit `ba06e2d69f51f62f6ea63386748bdbff1259cc58`.
* Built dedicated React Harvest workflows at `/operations/harvests`.
* Added collection filters `?farm_reference=` and `?crop_season_reference=` with AND semantics.
* Implemented server-side protection preventing harvest creation against closed or cancelled Crop Seasons.
* Added backend-supported `historical_locked` metadata preserving historical integrity when downstream production batches exist.
* Automated testing passed: 100 SQLite backend tests via `python manage.py test` (99 within `api` plus settings security), 13 Vitest tests, frontend lint, and production build.

---

## Known Operational Boundaries & Current Constraints

1. **Email Delivery Scope:** Personal Gmail SMTP with an App Password is used exclusively for low-volume development testing. It is not an enterprise transactional email service; Google rate limits and spam filters apply.
2. **SMS Verification Deferred:** Mobile numbers are stored in normalized E.164 format, but `mobile_verified` remains `false`. No SMS gateway is configured or called.
3. **Product Catalogue Unseeded:** The database contains 6 category labels and 0 products. No product records or specifications will be published until the owner completes review via the CSV intake template.
4. **Local Media Storage:** Product image uploads are stored locally under `backend/media/products/` and served by Django in DEBUG mode only. Cloud object storage (e.g. AWS S3 / Cloudflare R2) and CDN delivery remain to be configured for production.
5. **Throttling Cache:** Rate limits currently use Django's local-memory cache. A shared distributed cache (e.g. Redis) is required before multi-worker production deployment.

---

## Owner Confirmation Register (Open Launch Gates)

The following items are unresolved and require explicit owner confirmation before public commercial launch:

- [ ] **1. Legal Identity & Public Contact Details:** Registered company entity name, registration number, physical address, business phone, and public inquiry email.
- [ ] **2. Product Specifications & Photography:** Real product records, certified descriptions, and authentic photos submitted through [`docs/product-content-intake-template.csv`](docs/product-content-intake-template.csv).
- [ ] **3. Commercial Terms & Policies:** Minimum Order Quantities (MOQ), accepted Incoterms (FOB/CIF), export packaging specifications, payment terms, and response turnaround times.
- [ ] **4. Certifications & Compliance Claims:** Specific laboratory testing, APEDA/Spice Board registrations, or organic/quality certifications.
- [ ] **5. Production Transactional Email Provider:** Selection of an enterprise email service (AWS SES, SendGrid, Postmark, or Google Workspace relay) to replace test Gmail SMTP.
- [ ] **6. Privacy Policy Approval:** Legal approval of data controller identity, applicable jurisdiction (e.g. DPDP Act / GDPR), retention schedule, and final privacy notice.
- [ ] **7. Production Infrastructure:** Selection of production domain, SSL termination, managed MySQL hosting, and secure media storage.
