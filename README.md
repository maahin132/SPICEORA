# SPICEORA

**Tagline:** “From Indian Origins to Global Markets.”

SPICEORA is a premium, customer-facing Indian spice-export business website designed for international B2B buyers, importers, distributors, wholesalers, and commercial partners. The platform pairs a high-trust public marketing and product catalogue interface with an internal, private farm-to-inventory traceability and operations foundation.

The public website is intentionally tailored as a trade and export showcase—not a self-service consumer marketplace, SaaS dashboard, or generic ERP.

---

## Technology Stack

| Layer | Technologies & Versions | Purpose |
|---|---|---|
| **Frontend** | React 19 (`19.3.1`), Vite 8 (`8.3.5`), React Router 7 (`7.18.5`), Tailwind CSS 4 (`4.3.3`), Lucide React (`1.63.0`) | Client-rendered responsive SPA, editorial styling, and accessible UI components |
| **Backend** | Python 3.12, Django 5.2 (`5.2.18`), Django REST Framework (`3.16.1`), Pillow (`12.1.1`), phonenumbers (`9.0.17`) | REST APIs, authentication/authorization, file validation, and admin workflows |
| **Database** | MySQL 8.0 (development & target production), SQLite (isolated automated test suite) | Relational persistence, constraints, foreign-key protection, and transactional ledger |
| **Testing & Quality** | Vitest (`3.2.4`), React Testing Library (`16.3.0`), Oxlint (`1.89.0`), Django Test Framework | Fast unit tests, browser DOM assertions, static linting, and API integration coverage |
| **Authentication & Delivery** | Django session cookies, memory-held CSRF tokens, Gmail SMTP (TLS 587, low-volume test only) | Secure session authentication, PBKDF2 OTP hashing, and owner-approved email testing |

---

## Project Architecture & Core Features

* **Public Catalogue & Product Discovery:**
  * Dynamic, published-only product catalogue with category-based filtering and pagination (`/products/`, `/products/{slug}/`).
  * Six active candidate category labels: *Cumin*, *Fennel*, *Red chilli*, *Turmeric*, *Coriander*, and *Dhana-jeera*.
  * Zero seeded product records: products appear only after verified owner content and rights-cleared imagery are approved.
* **B2B Enquiry & Quotation System:**
  * Canonical enquiry route at [`/contact/`](./docs/INFORMATION_ARCHITECTURE.md) with preserved legacy `/enquiry/` URL redirects and query/hash parameters.
  * Contextual product preselection from catalogue detail pages.
  * Server-side input validation, rate limiting (5 submissions/hour/IP), and opaque confirmation receipts without exposing internal triage notes.
* **Email-First Customer Authentication:**
  * Customer registration activated exclusively via 6-digit email OTP challenges (`/register`, `/verify/email`).
  * E.164 phone numbers captured for verified record-keeping; mobile verification and SMS delivery are deferred (`mobile_verified` remains `false`).
  * Generic registration and recovery responses with a 1.0-second minimum timing floor to prevent account enumeration.
* **Private Staff Operations Dashboard:**
  * Session-authenticated, CSRF-enforced, model-permission-gated operations interface (`/operations/*`).
  * **Staff Enquiry Management:** Private inbox and detail view for enquiry triage, status updates (`new`, `in_progress`, `responded`, `closed`), and internal notes (`/operations/enquiries`).
  * **Farm Management:** Create, view, edit, and filter active and historical agricultural holdings (`/operations/farms`).
  * **Crop Season Management:** Track planting, growing, harvested, and closed seasons per farm with validated `farm_reference` filtering (`/operations/crop-seasons`).
  * **Harvest Management:** Record harvest dates, verified quantities, units, and historical locks with closed/cancelled season protection (`/operations/harvests`).
* **Farm-to-Inventory Traceability Ledger:**
  * Relational traceability chain: `Farm → CropSeason → Harvest → ProductionBatch → ProcessingRecord / InventoryMovement`.
  * Append-only inventory movements (production receipts, processing adjustments, reservations, dispatches, and approved corrections).
  * On-hand and available balances calculated dynamically from immutable movements under batch row locks.

---

## Current Status & Git Baseline

* **Branch:** `main` (tracked at `https://github.com/maahin132/SPICEORA`)
* **Completed Milestones:** **Phases 0 through 12** are fully implemented, verified, and merged.
* **Latest Release Commit:** `ba06e2d69f51f62f6ea63386748bdbff1259cc58` (*"Phase 12: complete harvest management"*)
* **Active Milestone:** **Phase 13 (Documentation Overhaul)**.
* **Operational Boundary:**
  * Email OTP delivery is verified using personal Gmail SMTP with an App Password for controlled low-volume development testing only. SMS is disabled.
  * No production product records or claims are published. Content intake proceeds via [`docs/product-content-intake-template.csv`](./docs/product-content-intake-template.csv).

---

## Developer Setup Instructions

### Path A: Isolated Testing Setup (< 3 Minutes)

This path requires **no database service installation** (no MySQL needed). It runs isolated in-memory SQLite backend tests and Vitest frontend tests.

#### 1. Backend Automated Tests (99 API tests + Settings Security)
From the repository root:
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py test --settings=config.test_settings
```

#### 2. Frontend Tests, Linter & Production Build
From a new terminal at the repository root:
```powershell
cd frontend
npm install
npm run test:run    # Runs 13 Vitest unit & integration tests
npm run lint        # Runs Oxlint across all JSX and JS files
npm run build       # Verifies production Vite bundling
```

---

### Path B: Full Local Development Setup (~15 Minutes)

This path sets up the live Django development server backed by local MySQL 8.0 and the Vite frontend dev proxy.

#### 1. Prerequisites
* Windows 10/11, Python 3.12+, Node.js 20+, npm 10+.
* MySQL 8.0.x running locally on port 3306.

#### 2. Configure Local Secrets (`.env`)
Copy the template to create a private local `.env` file at the repository root:
```powershell
Copy-Item .env.example .env
```
Open `.env` in your editor and configure:
1. `DJANGO_SECRET_KEY`: Replace with a secure random string (Django startup **fails fast** if left as the example placeholder or empty).
2. `DB_HOST`: Set to `localhost` (on Windows with MySQL 8 `caching_sha2_password`, `localhost` must be used to match the local account).
3. `DB_NAME`: `spiceora_db`
4. `DB_USER`: `spiceora_app`
5. `DB_PASSWORD`: Your local MySQL user password.
6. Gmail credentials (optional, for live OTP testing): `GOOGLE_SMTP_LOGIN` and `GOOGLE_SMTP_APP_PASSWORD` (Google 2-Step Verification App Password).

> [!WARNING]
> Never commit `.env` or credentials to version control. The `.env` file is untracked and ignored by Git.

#### 3. Initialize MySQL Database
Log in to MySQL as administrator and create the database and application user:
```sql
CREATE DATABASE IF NOT EXISTS spiceora_db CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER IF NOT EXISTS 'spiceora_app'@'localhost' IDENTIFIED BY 'YOUR_LOCAL_PASSWORD';
GRANT ALL PRIVILEGES ON spiceora_db.* TO 'spiceora_app'@'localhost';
FLUSH PRIVILEGES;
```

#### 4. Run Django Migrations & Start Backend Server
From `backend/`:
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```
Backend API will be available at `http://127.0.0.1:8000/api/` and health check at `http://127.0.0.1:8000/api/health/`.

#### 5. Start Frontend Development Server
From another terminal in `frontend/`:
```powershell
cd frontend
npm run dev
```
Open your browser at `http://127.0.0.1:5173/`. Vite proxies `/api` and `/media` requests directly to Django at `127.0.0.1:8000`.

---

## Documentation Navigation

Comprehensive planning, architecture, and operational specifications are maintained in the [`docs/`](./docs/) directory:

| Document | Description |
|---|---|
| [**Business Requirements**](./docs/BUSINESS_REQUIREMENTS.md) | Business scope, B2B user journeys, commercial boundaries, and owner rules |
| [**Architecture Plan**](./docs/ARCHITECTURE.md) | System topology, frontend component boundaries, and backend API structure |
| [**API Specification**](./docs/API.md) | Contracts for catalogue, enquiry, authentication, and operations endpoints |
| [**Database Plan**](./docs/DATABASE.md) | Model definitions, relational constraints, and inventory ledger balance calculations |
| [**Information Architecture**](./docs/INFORMATION_ARCHITECTURE.md) | Public sitemap, `/operations/*` route hierarchies, and navigation disclosure states |
| [**Visual Design Brief**](./docs/DESIGN_SYSTEM.md) | Brand color tokens (`#203B30`, `#F7F3E9`, `#C49A55`), typography, and editorial styling |
| [**Security Plan**](./docs/SECURITY.md) | Session security, CSRF protection, PBKDF2 OTP hashing, throttles, and secrets management |
| [**Testing Guide**](./docs/TESTING.md) | Verification suites, isolated SQLite testing, Vitest frontend specs, and QA protocols |
| [**Product Content Intake**](./docs/PRODUCT_CONTENT_PREPARATION.md) | Guidelines for authentic product photography, required specifications, and alt text |
| [**Product Intake Template (CSV)**](./docs/product-content-intake-template.csv) | Blank 6-category owner intake template (draft prompts only, unseeded) |
| [**Privacy Policy Framework**](./docs/PRIVACY_POLICY_FRAMEWORK.md) | *[Unpublished / Owner Review Required]* Legal data protection checklist |
| [**Deployment Plan**](./docs/DEPLOYMENT.md) | Production launch criteria, HTTPS/TLS termination, and infrastructure guidelines |
| [**Roadmap**](./docs/ROADMAP.md) | Milestone tracking across completed Phases 0–12 and upcoming features |
| [**Project Status**](./PROJECT_STATUS.md) | Verification logs, environment history, and current operational constraints |
| [**Changelog**](./CHANGELOG.md) | Detailed version history and phase-by-phase implementation logs |
| [**Contributing Guide**](./CONTRIBUTING.md) | Developer workflow, pre-PR verification checklist, and Git conventions |

---

## License & Ownership

Proprietary. All rights reserved by **SPICEORA**. Unauthorized duplication, distribution, or public publishing of unverified company claims is strictly prohibited.
